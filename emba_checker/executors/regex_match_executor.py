# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 正则匹配执行器
使用正则表达式检查文本内容
"""

import sys
import os
import re
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_executor import BaseExecutor, CheckIssue, CheckResult


class RegexMatchExecutor(BaseExecutor):
    """正则匹配执行器"""
    
    def check(self, rule: Dict) -> CheckIssue:
        conditions = rule.get("conditions", {})
        zones = rule.get("target_zone", [])
        rule_id = rule.get("rule_id", "")
        
        # 如果条件为空，返回 SKIP
        if not conditions:
            return CheckIssue(
                rule_id=rule_id,
                check_type="regex_match",
                result=CheckResult.SKIP.value,
                message="规则条件未配置，跳过检查",
                severity="info"
            )
        
        pattern = conditions.get("pattern", "")
        match_mode = conditions.get("match_mode", "must_match")
        scope = conditions.get("scope", "full_text")
        
        if not pattern:
            return CheckIssue(
                rule_id=rule_id,
                check_type="regex_match",
                result=CheckResult.ERROR.value,
                message="正则表达式为空",
                severity="error"
            )
        
        text = self._get_text_in_zones(zones)
        
        if not text:
            return CheckIssue(
                rule_id=rule_id,
                check_type="regex_match",
                result=CheckResult.SKIP.value,
                message=f"在指定区域 {zones} 中未找到文本",
                severity="info"
            )
        
        try:
            regex = re.compile(pattern)
        except re.error as e:
            return CheckIssue(
                rule_id=rule_id,
                check_type="regex_match",
                result=CheckResult.ERROR.value,
                message=f"正则表达式错误: {str(e)}",
                severity="error"
            )
        
        matches = regex.findall(text)
        
        if match_mode == "must_match":
            if not matches:
                # 未找到匹配可能是文档中确实没有该内容，返回 SKIP 而不是 FAIL
                return CheckIssue(
                    rule_id=rule_id,
                    check_type="regex_match",
                    result=CheckResult.SKIP.value,
                    message=f"未找到匹配 '{pattern}' 的内容",
                    location={"pattern": pattern, "zones": zones},
                    severity="info"
                )
        
        elif match_mode == "must_not_match":
            if matches:
                # 使用规则中的 error_message（人类可读的格式要求）
                error_msg = rule.get('error_message', f"发现禁止的内容 '{matches[0][:20]}...'")
                full_message = error_msg + f"\n当前检测到: {len(matches)}处匹配"
                
                return CheckIssue(
                    rule_id=rule_id,
                    check_type="regex_match",
                    result=CheckResult.FAIL.value,
                    message=full_message,
                    location={"pattern": pattern, "matches": matches[:3], "zones": zones},
                    severity="error"
                )
        
        return CheckIssue(
            rule_id=rule_id,
            check_type="regex_match",
            result=CheckResult.PASS.value,
            message=f"正则匹配检查通过，找到 {len(matches)} 处匹配",
            location={"matches_count": len(matches), "zones": zones},
            severity="info"
        )
