# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 文本匹配执行器
检查固定格式文本是否与模板一致
"""

import sys
import os
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_executor import BaseExecutor, CheckIssue, CheckResult


class TextMatchExecutor(BaseExecutor):
    """文本匹配执行器"""
    
    def check(self, rule: Dict) -> CheckIssue:
        conditions = rule.get("conditions", {})
        zones = rule.get("target_zone", [])
        rule_id = rule.get("rule_id", "")
        
        # 如果条件为空，返回 SKIP
        if not conditions:
            return CheckIssue(
                rule_id=rule_id,
                check_type="text_match",
                result=CheckResult.SKIP.value,
                message="规则条件未配置，跳过检查",
                severity="info"
            )
        
        expected_text = conditions.get("expected_text", "")
        match_mode = conditions.get("match_mode", "exact")
        
        text = self._get_text_in_zones(zones)
        
        # 如果没有找到文本，返回 SKIP 而不是 error
        if not text:
            return CheckIssue(
                rule_id=rule_id,
                check_type="text_match",
                result=CheckResult.SKIP.value,
                message=f"在指定区域 {zones} 中未找到文本",
                severity="info"
            )
        
        # 如果没有设置 expected_text，也返回 SKIP
        if not expected_text.strip():
            return CheckIssue(
                rule_id=rule_id,
                check_type="text_match",
                result=CheckResult.SKIP.value,
                message="未设置检查文本，跳过",
                severity="info"
            )
        
        if match_mode == "exact":
            if expected_text.strip() != text.strip():
                # 使用规则中的 error_message（人类可读的格式要求）
                error_msg = rule.get('error_message', "文本不匹配")
                full_message = error_msg + f"\n当前检测到: {text[:50]}..."
                
                return CheckIssue(
                    rule_id=rule_id,
                    check_type="text_match",
                    result=CheckResult.FAIL.value,
                    message=full_message,
                    location={"expected": expected_text[:50], "actual": text[:50]},
                    severity="error"
                )
        
        elif match_mode == "contains":
            if expected_text not in text:
                # 使用规则中的 error_message
                error_msg = rule.get('error_message', f"未找到预期文本 '{expected_text[:30]}...'")
                full_message = error_msg + f"\n当前检测到: (未找到该文本)"
                
                return CheckIssue(
                    rule_id=rule_id,
                    check_type="text_match",
                    result=CheckResult.FAIL.value,
                    message=full_message,
                    location={"expected": expected_text},
                    severity="error"
                )
        
        elif match_mode == "not_contains":
            if expected_text in text:
                # 使用规则中的 error_message
                error_msg = rule.get('error_message', f"发现禁止文本 '{expected_text[:30]}...'")
                full_message = error_msg + f"\n当前检测到: {text[:50]}..."
                
                return CheckIssue(
                    rule_id=rule_id,
                    check_type="text_match",
                    result=CheckResult.FAIL.value,
                    message=full_message,
                    location={"forbidden": expected_text},
                    severity="error"
                )
        
        return CheckIssue(
            rule_id=rule_id,
            check_type="text_match",
            result=CheckResult.PASS.value,
            message="文本匹配检查通过",
            location={"zones": zones},
            severity="info"
        )
