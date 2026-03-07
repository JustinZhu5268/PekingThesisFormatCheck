# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 交叉引用执行器
检查图表编号与引用的一致性
"""

import sys
import os
import re
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_executor import BaseExecutor, CheckIssue, CheckResult


class CrossReferenceExecutor(BaseExecutor):
    """交叉引用执行器"""
    
    def check(self, rule: Dict) -> CheckIssue:
        conditions = rule.get("conditions", {})
        rule_id = rule.get("rule_id", "")
        
        # 如果条件为空，返回 SKIP
        if not conditions:
            return CheckIssue(
                rule_id=rule_id,
                check_type="cross_reference",
                result=CheckResult.SKIP.value,
                message="规则条件未配置，跳过检查",
                severity="info"
            )
        
        zones = conditions.get("zones", ["body_chapter", "references"])
        
        body_text = self._get_text_in_zones([z for z in zones if z != "references"])
        ref_text = self._get_text_in_zones(["references"])
        
        if not body_text and not ref_text:
            return CheckIssue(
                rule_id=rule_id,
                check_type="cross_reference",
                result=CheckResult.SKIP.value,
                message="未找到正文或参考文献文本",
                severity="info"
            )
        
        fig_pattern = r'图\s*(\d+\.\d+)'
        table_pattern = r'表\s*(\d+\.\d+)'
        
        body_figs = set(re.findall(fig_pattern, body_text))
        body_tables = set(re.findall(table_pattern, body_text))
        
        ref_figs = set(re.findall(fig_pattern, ref_text))
        ref_tables = set(re.findall(table_pattern, ref_text))
        
        errors = []
        
        if conditions.get("error_on") in ["both", "body"]:
            missing_ref = (body_figs | body_tables) - (ref_figs | ref_tables)
            if missing_ref:
                errors.append(f"正文引用但参考文献中未列出: {missing_ref}")
        
        if conditions.get("error_on") in ["both", "ref"]:
            orphan_ref = (ref_figs | ref_tables) - (body_figs | body_tables)
            if orphan_ref:
                errors.append(f"参考文献列出但正文未引用: {orphan_ref}")
        
        if errors:
            # 使用规则中的 error_message（人类可读的格式要求）
            error_msg = rule.get('error_message', f"交叉引用检查失败: {'; '.join(errors)}")
            full_message = error_msg
            
            return CheckIssue(
                rule_id=rule_id,
                check_type="cross_reference",
                result=CheckResult.FAIL.value,
                message=full_message,
                location={"body_figs": list(body_figs), "ref_figs": list(ref_figs)},
                severity="error"
            )
        
        return CheckIssue(
            rule_id=rule_id,
            check_type="cross_reference",
            result=CheckResult.PASS.value,
            message="交叉引用检查通过",
            location={"body_figs": len(body_figs), "ref_figs": len(ref_figs)},
            severity="info"
        )
