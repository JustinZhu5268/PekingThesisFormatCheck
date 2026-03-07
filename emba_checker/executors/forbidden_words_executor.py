# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 禁用词执行器
检查文本中是否包含禁用词或口语化词
"""

import sys
import os
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_executor import BaseExecutor, CheckIssue, CheckResult
import utils


class ForbiddenWordsExecutor(BaseExecutor):
    """禁用词执行器"""
    
    def check(self, rule: Dict) -> CheckIssue:
        conditions = rule.get("conditions", {})
        zones = rule.get("target_zone", [])
        rule_id = rule.get("rule_id", "")
        
        # 如果条件为空，返回 SKIP
        if not conditions:
            return CheckIssue(
                rule_id=rule_id,
                check_type="forbidden_words",
                result=CheckResult.SKIP.value,
                message="规则条件未配置，跳过检查",
                severity="info"
            )
        
        inline_words = conditions.get("inline_words", [])
        word_list_file = conditions.get("word_list_file", "")
        match_mode = conditions.get("match_mode", "any")
        
        if word_list_file:
            words = utils.load_word_list(
                os.path.join(os.path.dirname(__file__), "..", "word_lists", word_list_file)
            )
            inline_words.extend(words)
        
        if not inline_words:
            return CheckIssue(
                rule_id=rule_id,
                check_type="forbidden_words",
                result=CheckResult.SKIP.value,
                message="未配置禁用词列表",
                severity="info"
            )
        
        text = self._get_text_in_zones(zones)
        
        if not text:
            return CheckIssue(
                rule_id=rule_id,
                check_type="forbidden_words",
                result=CheckResult.SKIP.value,
                message=f"在指定区域 {zones} 中未找到文本",
                severity="info"
            )
        
        found_words = []
        for word in inline_words:
            if word in text:
                found_words.append(word)
        
        if match_mode == "not_contains":
            if found_words:
                # 使用规则中的 error_message（人类可读的格式要求）
                error_msg = rule.get('error_message', f"发现禁用词: {', '.join(found_words[:5])}")
                full_message = error_msg + f"\n当前检测到: {', '.join(found_words[:5])}"
                
                return CheckIssue(
                    rule_id=rule_id,
                    check_type="forbidden_words",
                    result=CheckResult.FAIL.value,
                    message=full_message,
                    location={"found_words": found_words[:10], "zones": zones},
                    severity="error"
                )
        
        elif match_mode == "any":
            if found_words:
                # 使用规则中的 error_message
                error_msg = rule.get('error_message', f"发现禁用词: {', '.join(found_words[:5])}")
                full_message = error_msg + f"\n当前检测到: {', '.join(found_words[:5])}"
                
                return CheckIssue(
                    rule_id=rule_id,
                    check_type="forbidden_words",
                    result=CheckResult.PASS.value,
                    message=full_message,
                    location={"found_words": found_words[:10], "zones": zones},
                    severity="warning"
                )
        
        return CheckIssue(
            rule_id=rule_id,
            check_type="forbidden_words",
            result=CheckResult.PASS.value,
            message="禁用词检查通过",
            location={"zones": zones},
            severity="info"
        )
