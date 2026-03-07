# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - Claude AI 语义检查引擎
调用 Claude Sonnet 4.5 API 进行语义检查
"""

import os
import sys
import json
import threading
import time
from typing import List, Dict, Any, Optional, Callable
from docx.document import Document

# 添加项目根目录到路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)


class ClaudeEngine:
    """
    Claude AI 语义检查引擎
    
    负责：
    1. 调用 Claude API 进行语义检查
    2. 按区域批量发送逻辑
    3. 超时处理和错误降级
    4. Claude 开关控制
    """
    
    # 支持的模型
    DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
    
    # 超时设置
    SINGLE_CALL_TIMEOUT = 30  # 单次调用超时（秒）
    TOTAL_TIMEOUT = 120  # 总超时（秒）
    
    def __init__(self, doc: Document, rules: List[Dict], zone_map: Dict[int, str], 
                 api_key: Optional[str] = None,
                 progress_callback: Optional[Callable] = None):
        self.doc = doc
        self.rules = rules
        self.zone_map = zone_map
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.progress_callback = progress_callback
        self.issues: List[Any] = []
        self.execution_log: List[str] = []
        self.client = None
        self.enabled = bool(self.api_key)
        
        # 初始化 Claude 客户端
        if self.enabled:
            self._init_client()
    
    def _init_client(self):
        """初始化 Claude 客户端"""
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            self._log("Warning: anthropic package not installed")
            self.enabled = False
        except Exception as e:
            self._log(f"Warning: Failed to initialize Claude client: {e}")
            self.enabled = False
    
    def _log(self, message: str):
        """记录日志"""
        self.execution_log.append(message)
    
    def _report_progress(self, message: str, current: int = None, total: int = None):
        """报告进度"""
        if self.progress_callback:
            self.progress_callback("Claude", message, current, total)
        self._log(message)
    
    def run_all(self) -> List[Any]:
        """运行所有 Claude 语义检查"""
        self.issues = []
        
        if not self.enabled:
            self._report_progress("Claude API 未启用，跳过语义检查")
            return self.issues
        
        # 获取所有 ai_semantic 类型的规则
        ai_rules = [r for r in self.rules 
                   if r.get("check_type") == "ai_semantic" 
                   and r.get("enabled", True)]
        
        if not ai_rules:
            self._report_progress("无 AI 语义检查规则，跳过")
            return self.issues
        
        self._report_progress(f"开始 AI 语义检查 ({len(ai_rules)} 条规则)", 0, len(ai_rules))
        
        # 按区域分组规则
        rules_by_zone = self._group_rules_by_zone(ai_rules)
        
        # 逐区域执行检查
        for zone, zone_rules in rules_by_zone.items():
            zone_issues = self._check_zone(zone, zone_rules)
            self.issues.extend(zone_issues)
        
        self._report_progress(f"AI 语义检查完成，发现 {len(self.issues)} 个问题", len(ai_rules), len(ai_rules))
        
        return self.issues
    
    def _group_rules_by_zone(self, rules: List[Dict]) -> Dict[str, List[Dict]]:
        """按区域分组规则"""
        grouped = {}
        
        for rule in rules:
            zones = rule.get("target_zone", [])
            for zone in zones:
                if zone not in grouped:
                    grouped[zone] = []
                grouped[zone].append(rule)
        
        return grouped
    
    def _check_zone(self, zone: str, rules: List[Dict]) -> List[Any]:
        """检查单个区域"""
        issues = []
        
        # 获取区域文本
        zone_text = self._get_text_in_zone(zone)
        
        if not zone_text:
            self._report_progress(f"区域 {zone} 无文本，跳过")
            return issues
        
        # 限制文本长度
        max_length = 10000  # Claude 输入长度限制
        if len(zone_text) > max_length:
            zone_text = zone_text[:max_length] + "...(truncated)"
        
        self._report_progress(f"检查区域 {zone} ({len(zone_text)} 字符)")
        
        # 逐规则检查
        for rule in rules:
            rule_issue = self._check_single_rule(rule, zone_text, zone)
            if rule_issue:
                issues.append(rule_issue)
        
        return issues
    
    def _check_single_rule(self, rule: Dict, text: str, zone: str) -> Optional[Any]:
        """检查单条规则"""
        from base_executor import CheckIssue
        
        conditions = rule.get("conditions", {})
        rule_id = rule.get("rule_id", "")
        prompt_template = conditions.get("prompt_template", "")
        
        if not prompt_template:
            return CheckIssue(
                rule_id=rule_id,
                check_type="ai_semantic",
                result="error",
                message="未配置 prompt 模板",
                severity="error"
            )
        
        # 构建 prompt
        prompt = prompt_template.replace("{text}", text)
        
        # 添加格式要求
        format_spec = conditions.get("format_spec", {})
        if format_spec:
            prompt += f"\n\n请以 JSON 格式返回结果，字段包括: {', '.join(format_spec.keys())}"
        
        try:
            # 调用 Claude API
            response = self.client.messages.create(
                model=self.DEFAULT_MODEL,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
                timeout=self.SINGLE_CALL_TIMEOUT,
            )
            
            result_text = response.content[0].text
            
            # 解析结果
            return self._parse_result(rule, result_text, zone)
            
        except Exception as e:
            error_msg = str(e)
            self._report_progress(f"规则 {rule_id} 执行出错: {error_msg[:50]}")
            
            return CheckIssue(
                rule_id=rule_id,
                check_type="ai_semantic",
                result="error",
                message=f"AI 检查出错: {error_msg[:100]}",
                severity="warning"
            )
    
    def _parse_result(self, rule: Dict, result_text: str, zone: str) -> Optional[Any]:
        """解析 Claude 返回结果"""
        from base_executor import CheckIssue
        
        rule_id = rule.get("rule_id", "")
        
        # 尝试解析 JSON
        try:
            # 提取 JSON 部分
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                result = json.loads(json_str)
            else:
                result = {}
        except json.JSONDecodeError:
            result = {}
        
        # 判断是否通过
        # 检查是否有明确的失败标志
        fail_keywords = ["false", "no", "不通过", "不符合", "错误", "缺失"]
        
        is_pass = not any(kw in result_text.lower() for kw in fail_keywords)
        
        if is_pass:
            return CheckIssue(
                rule_id=rule_id,
                check_type="ai_semantic",
                result="pass",
                message="AI 语义检查通过",
                location={"zone": zone, "result": result},
                severity="info"
            )
        else:
            return CheckIssue(
                rule_id=rule_id,
                check_type="ai_semantic",
                result="fail",
                message=f"AI 检查发现问题",
                location={"zone": zone, "result": result},
                severity="warning"
            )
    
    def _get_text_in_zone(self, zone: str) -> str:
        """获取指定区域的文本"""
        texts = []
        
        for i, para in enumerate(self.doc.paragraphs):
            para_zone = self.zone_map.get(i, "unknown")
            if para_zone == zone:
                texts.append(para.text)
        
        return "\n".join(texts)
    
    def run_async(self) -> List[Any]:
        """异步运行（用于 GUI）"""
        issues = []
        error_issue = None
        
        def worker():
            nonlocal issues, error_issue
            try:
                issues = self.run_all()
            except Exception as e:
                error_issue = e
        
        thread = threading.Thread(target=worker)
        thread.start()
        thread.join(timeout=self.TOTAL_TIMEOUT)
        
        if thread.is_alive():
            self._report_progress("AI 语义检查超时")
            return []
        
        if error_issue:
            self._report_progress(f"AI 语义检查出错: {str(error_issue)}")
            return []
        
        return issues
    
    def is_enabled(self) -> bool:
        """检查是否启用"""
        return self.enabled
    
    def get_summary(self) -> Dict[str, Any]:
        """获取检查摘要"""
        return {
            "enabled": self.enabled,
            "total_issues": len(self.issues),
            "by_severity": {
                "error": 0,
                "warning": 0,
                "info": 0,
            },
        }


def run_claude_engine(doc: Document, rules: List[Dict], zone_map: Dict[int, str],
                      api_key: Optional[str] = None,
                      progress_callback: Optional[Callable] = None) -> List[Any]:
    """
    运行 Claude 引擎的便捷函数
    
    Args:
        doc: Document 对象
        rules: 规则列表
        zone_map: 区域映射
        api_key: 可选的 API Key
        progress_callback: 进度回调函数
        
    Returns:
        List[Any]: 检查问题列表
    """
    engine = ClaudeEngine(doc, rules, zone_map, api_key, progress_callback)
    return engine.run_all()
