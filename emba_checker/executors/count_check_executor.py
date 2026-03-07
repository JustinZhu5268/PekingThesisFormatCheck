# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 计数检查执行器
统计字数、段落数、参考文献数等
"""

import sys
import os
import re
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_executor import BaseExecutor, CheckIssue, CheckResult
import utils


class CountCheckExecutor(BaseExecutor):
    """计数检查执行器"""
    
    def check(self, rule: Dict) -> CheckIssue:
        conditions = rule.get("conditions", {})
        zones = rule.get("target_zone", [])
        rule_id = rule.get("rule_id", "")
        
        # 如果条件为空，返回 SKIP
        if not conditions:
            return CheckIssue(
                rule_id=rule_id,
                check_type="count_check",
                result=CheckResult.SKIP.value,
                message="规则条件未配置，跳过检查",
                severity="info"
            )
        
        count_type = conditions.get("count_type", "chinese_chars")
        
        # 获取文本或段落
        if count_type == "paragraphs":
            paragraphs = self._get_paragraphs_in_zones(zones)
            count = len([p for p in paragraphs if p[1].text.strip()])
        else:
            text = self._get_text_in_zones(zones)
            
            if count_type == "chinese_chars":
                count = utils.count_chinese_chars(text)
            elif count_type == "total_chars":
                count = utils.count_total_chars(text)
            elif count_type == "words":
                count = utils.count_words(text)
            elif count_type == "references":
                count = len(re.findall(r'^\s*\[\d+\]', text, re.MULTILINE))
            else:
                count = len(text)
        
        # 获取限制条件
        min_value = conditions.get("min_value")
        max_value = conditions.get("max_value")
        
        errors = []
        
        if min_value is not None and count < min_value:
            errors.append(f"计数 {count} 少于最小值 {min_value}")
        
        if max_value is not None and count > max_value:
            errors.append(f"计数 {count} 超过最大值 {max_value}")
        
        if errors:
            # 使用规则中的 error_message（人类可读的格式要求）
            error_msg = rule.get('error_message', f"{count_type} 计数检查失败: {'; '.join(errors)}")
            full_message = error_msg + f"\n当前检测到: {count}"
            
            return CheckIssue(
                rule_id=rule_id,
                check_type="count_check",
                result=CheckResult.FAIL.value,
                message=full_message,
                location={"count": count, "min": min_value, "max": max_value, "zones": zones},
                severity="error"
            )
        
        return CheckIssue(
            rule_id=rule_id,
            check_type="count_check",
            result=CheckResult.PASS.value,
            message=f"{count_type} 计数检查通过: {count}",
            location={"count": count, "zones": zones},
            severity="info"
        )
