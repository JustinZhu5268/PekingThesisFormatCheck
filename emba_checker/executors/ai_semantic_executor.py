# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - AI 语义执行器
调用 Claude API 进行语义检查
"""

import sys
import os
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_executor import BaseExecutor, CheckIssue, CheckResult


class AISemanticExecutor(BaseExecutor):
    """AI 语义执行器"""
    
    def __init__(self, doc, rules, zone_map, api_key=None):
        super().__init__(doc, rules, zone_map)
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                pass
    
    def check(self, rule: Dict) -> CheckIssue:
        conditions = rule.get("conditions", {})
        zones = rule.get("target_zone", [])
        rule_id = rule.get("rule_id", "")
        
        # 如果条件为空，返回 SKIP
        if not conditions:
            return CheckIssue(
                rule_id=rule_id,
                check_type="ai_semantic",
                result=CheckResult.SKIP.value,
                message="规则条件未配置，跳过检查",
                severity="info"
            )
        
        if not self.client:
            return CheckIssue(
                rule_id=rule_id,
                check_type="ai_semantic",
                result=CheckResult.SKIP.value,
                message="未配置 Claude API Key",
                severity="info"
            )
        
        prompt_template = conditions.get("prompt_template", "")
        
        if not prompt_template:
            return CheckIssue(
                rule_id=rule_id,
                check_type="ai_semantic",
                result=CheckResult.ERROR.value,
                message="未配置 prompt 模板",
                severity="error"
            )
        
        text = self._get_text_in_zones(zones)
        
        if not text:
            return CheckIssue(
                rule_id=rule_id,
                check_type="ai_semantic",
                result=CheckResult.SKIP.value,
                message=f"在指定区域 {zones} 中未找到文本",
                severity="info"
            )
        
        prompt = prompt_template.replace("{text}", text[:5000])
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text
            
            if "false" in result_text.lower() or "error" in result_text.lower():
                # 使用规则中的 error_message（人类可读的格式要求）
                error_msg = rule.get('error_message', "AI 检查发现问题")
                full_message = error_msg + f"\nAI 分析: {result_text[:200]}"
                
                return CheckIssue(
                    rule_id=rule_id,
                    check_type="ai_semantic",
                    result=CheckResult.FAIL.value,
                    message=full_message,
                    location={"ai_response": result_text[:200], "zones": zones},
                    severity="warning"
                )
            
            return CheckIssue(
                rule_id=rule_id,
                check_type="ai_semantic",
                result=CheckResult.PASS.value,
                message="AI 语义检查通过",
                location={"ai_response": result_text[:200], "zones": zones},
                severity="info"
            )
            
        except Exception as e:
            return CheckIssue(
                rule_id=rule_id,
                check_type="ai_semantic",
                result=CheckResult.ERROR.value,
                message=f"AI 检查出错: {str(e)[:100]}",
                severity="error"
            )
