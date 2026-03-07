# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 调度器模块
协调 DocxEngine + ClaudeEngine，执行 Issue 合并去重
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional, Callable, Tuple
from datetime import datetime

# 添加项目根目录到路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from docx import Document


class MainEngine:
    """
    主调度器
    
    负责：
    1. 协调 DocxEngine + ClaudeEngine
    2. Issue 去重和合并
    3. 提供统一入口
    """
    
    def __init__(self, doc_path: str, rules_path: Optional[str] = None, 
                 api_key: Optional[str] = None,
                 progress_callback: Optional[Callable] = None):
        self.doc_path = doc_path
        self.api_key = api_key
        self.progress_callback = progress_callback
        
        # 加载文档
        self.doc = Document(doc_path)
        
        # 加载规则
        if rules_path is None:
            rules_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rules_registry.json")
        
        with open(rules_path, 'r', encoding='utf-8') as f:
            self.rules = json.load(f)
        
        # 初始化区域检测器
        from emba_checker.zone_detector import detect_zones
        self.zone_map = detect_zones(self.doc)
        
        # Issue 列表
        self.issues: List[Any] = []
        
        # 统计信息
        self.stats = {
            "docx_engine_issues": 0,
            "claude_engine_issues": 0,
            "deduplicated": 0,
            "total_time": 0,
        }
    
    def _report_progress(self, source: str, message: str, current: int = None, total: int = None):
        """报告进度"""
        if self.progress_callback:
            self.progress_callback(source, message, current, total)
    
    def run(self, enable_claude: bool = True) -> List[Any]:
        """
        运行完整审查流程
        
        Args:
            enable_claude: 是否启用 Claude AI 检查
            
        Returns:
            List[Any]: 合并后的 Issue 列表
        """
        start_time = datetime.now()
        
        # Step 1: 运行 DocxEngine（确定性检查）
        self._report_progress("主引擎", "开始确定性检查...", 0, 100)
        docx_issues = self._run_docx_engine()
        self.stats["docx_engine_issues"] = len(docx_issues)
        
        # Step 2: 运行 ClaudeEngine（AI 语义检查）
        claude_issues = []
        if enable_claude and self.api_key:
            self._report_progress("主引擎", "开始 AI 语义检查...", 50, 100)
            claude_issues = self._run_claude_engine()
            self.stats["claude_engine_issues"] = len(claude_issues)
        else:
            self._report_progress("主引擎", "跳过 AI 语义检查", 50, 100)
        
        # Step 3: 合并 Issue
        self._report_progress("主引擎", "合并检查结果...", 80, 100)
        self.issues = self._merge_issues(docx_issues, claude_issues)
        
        # 记录时间
        self.stats["total_time"] = (datetime.now() - start_time).total_seconds()
        
        self._report_progress("主引擎", f"审查完成，共 {len(self.issues)} 个问题", 100, 100)
        
        return self.issues
    
    def _run_docx_engine(self) -> List[Any]:
        """运行 DocxEngine"""
        from emba_checker.docx_engine import DocxEngine
        
        engine = DocxEngine(
            self.doc, 
            self.rules, 
            self.zone_map,
            self._make_docx_progress_callback()
        )
        
        return engine.run_all()
    
    def _run_claude_engine(self) -> List[Any]:
        """运行 ClaudeEngine"""
        from emba_checker.claude_engine import ClaudeEngine
        
        engine = ClaudeEngine(
            self.doc,
            self.rules,
            self.zone_map,
            self.api_key,
            self._make_claude_progress_callback()
        )
        
        if not engine.is_enabled():
            self._report_progress("Claude", "API 未配置，跳过")
            return []
        
        return engine.run_all()
    
    def _make_docx_progress_callback(self) -> Callable:
        """创建 DocxEngine 进度回调"""
        def callback(group: str, message: str, current: int, total: int):
            self._report_progress("确定性检查", f"[{group}] {message}", current, total)
        return callback
    
    def _make_claude_progress_callback(self) -> Callable:
        """创建 ClaudeEngine 进度回调"""
        def callback(source: str, message: str, current: int, total: int):
            self._report_progress("AI 语义检查", message, current, total)
        return callback
    
    def _merge_issues(self, docx_issues: List[Any], claude_issues: List[Any]) -> List[Any]:
        """
        合并 Issue
        
        策略：
        1. 相同 rule_id 的 Issue 合并
        2. 保留最严重的结果
        3. 合并 location 信息
        """
        # 按 rule_id 分组
        issues_by_rule = {}
        
        # 添加 DocxEngine 的 Issue
        for issue in docx_issues:
            rule_id = getattr(issue, 'rule_id', 'unknown')
            if rule_id not in issues_by_rule:
                issues_by_rule[rule_id] = []
            issues_by_rule[rule_id].append(issue)
        
        # 添加 ClaudeEngine 的 Issue（用于补充）
        for issue in claude_issues:
            rule_id = getattr(issue, 'rule_id', 'unknown')
            if rule_id not in issues_by_rule:
                issues_by_rule[rule_id] = []
            issues_by_rule[rule_id].append(issue)
        
        # 合并每个 rule_id 的 Issue
        merged = []
        
        for rule_id, rule_issues in issues_by_rule.items():
            if len(rule_issues) == 1:
                merged.append(rule_issues[0])
            else:
                # 多个 Issue，合并
                merged_issue = self._merge_duplicate_issues(rule_issues)
                merged.append(merged_issue)
        
        # 计算去重数量
        original_count = len(docx_issues) + len(claude_issues)
        self.stats["deduplicated"] = original_count - len(merged)
        
        return merged
    
    def _merge_duplicate_issues(self, issues: List[Any]) -> Any:
        """
        合并重复的 Issue
        
        规则：
        1. 优先保留 error > warning > info
        2. 合并 location 信息
        3. 合并 message
        """
        from emba_checker.base_executor import CheckIssue
        
        # 获取最严重的结果
        severity_order = {'error': 0, 'warning': 1, 'info': 2, 'skip': 3}
        
        most_severe = min(issues, key=lambda x: severity_order.get(getattr(x, 'severity', 'info'), 3))
        
        # 合并 location
        locations = []
        for issue in issues:
            loc = getattr(issue, 'location', None)
            if loc:
                locations.append(loc)
        
        merged_location = locations[0] if locations else {}
        if len(locations) > 1:
            merged_location['_merged'] = True
            merged_location['_locations'] = locations
        
        # 合并 message
        messages = [getattr(i, 'message', '') for i in issues]
        merged_message = messages[0]
        if len(set(messages)) > 1:
            merged_message = f"{messages[0]} [另有 {len(messages)-1} 条类似问题]"
        
        return CheckIssue(
            rule_id=getattr(most_severe, 'rule_id', 'unknown'),
            check_type=getattr(most_severe, 'check_type', 'unknown'),
            result=getattr(most_severe, 'result', 'unknown'),
            message=merged_message,
            location=merged_location,
            severity=getattr(most_severe, 'severity', 'info'),
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """获取审查摘要"""
        error_count = sum(1 for i in self.issues if getattr(i, 'severity', '') == 'error')
        warning_count = sum(1 for i in self.issues if getattr(i, 'severity', '') == 'warning')
        info_count = sum(1 for i in self.issues if getattr(i, 'severity', '') == 'info')
        
        return {
            "total_issues": len(self.issues),
            "error_count": error_count,
            "warning_count": warning_count,
            "info_count": info_count,
            "docx_engine_issues": self.stats["docx_engine_issues"],
            "claude_engine_issues": self.stats["claude_engine_issues"],
            "deduplicated": self.stats["deduplicated"],
            "total_time": self.stats["total_time"],
        }
    
    def export_issues_json(self, output_path: str):
        """导出 Issue 到 JSON"""
        issues_data = []
        
        for issue in self.issues:
            issues_data.append({
                "rule_id": getattr(issue, 'rule_id', ''),
                "check_type": getattr(issue, 'check_type', ''),
                "result": getattr(issue, 'result', ''),
                "message": getattr(issue, 'message', ''),
                "severity": getattr(issue, 'severity', ''),
                "location": getattr(issue, 'location', {}),
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(issues_data, f, ensure_ascii=False, indent=2)


def main():
    """主入口函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='北大光华 EMBA 论文格式审查工具')
    parser.add_argument('input_file', help='输入的 Word 文档路径')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-r', '--rules', help='规则文件路径')
    parser.add_argument('-k', '--api-key', help='Claude API Key')
    parser.add_argument('--no-claude', action='store_true', help='禁用 AI 语义检查')
    parser.add_argument('--export-json', help='导出 Issue 到 JSON 文件')
    
    args = parser.parse_args()
    
    # 检查输入文件
    if not os.path.exists(args.input_file):
        print(f"错误：输入文件不存在: {args.input_file}")
        return 1
    
    # 进度回调
    def progress_callback(source, message, current, total):
        if total:
            print(f"[{source}] {message} ({current}/{total})")
        else:
            print(f"[{source}] {message}")
    
    # 创建引擎
    engine = MainEngine(
        args.input_file,
        args.rules,
        args.api_key,
        progress_callback
    )
    
    # 运行审查
    issues = engine.run(enable_claude=not args.no_claude)
    
    # 输出摘要
    summary = engine.get_summary()
    
    print("\n" + "=" * 50)
    print("审查完成")
    print("=" * 50)
    print(f"发现问题总数: {summary['total_issues']}")
    print(f"  错误: {summary['error_count']}")
    print(f"  警告: {summary['warning_count']}")
    print(f"  信息: {summary['info_count']}")
    print(f"确定性检查: {summary['docx_engine_issues']} 条")
    print(f"AI 语义检查: {summary['claude_engine_issues']} 条")
    print(f"去重合并: {summary['deduplicated']} 条")
    print(f"总耗时: {summary['total_time']:.2f} 秒")
    print("=" * 50)
    
    # 导出 JSON
    if args.export_json:
        engine.export_issues_json(args.export_json)
        print(f"\n已导出 Issue 到: {args.export_json}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
