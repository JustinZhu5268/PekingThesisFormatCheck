# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 全局属性执行器
检查页面设置、页边距、纸张尺寸等全局属性
"""

import sys
import os
from typing import Dict

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_executor import BaseExecutor, CheckIssue, CheckResult
import utils


class GlobalPropertyExecutor(BaseExecutor):
    """全局属性执行器"""
    
    def check(self, rule: Dict) -> CheckIssue:
        conditions = rule.get("conditions", {})
        rule_id = rule.get("rule_id", "")
        
        # 如果条件为空，返回 SKIP
        if not conditions:
            return CheckIssue(
                rule_id=rule_id,
                check_type="global_property",
                result=CheckResult.SKIP.value,
                message="规则条件未配置，跳过检查",
                severity="info"
            )
        
        errors = []
        
        for section_idx, section in enumerate(self.doc.sections):
            if "page_width_cm" in conditions or "page_height_cm" in conditions:
                page_size = utils.get_page_size(section)
                expected_width = conditions.get("page_width_cm", 21.0)
                expected_height = conditions.get("page_height_cm", 29.7)
                
                if abs(page_size['width_cm'] - expected_width) > 0.1:
                    errors.append(f"节 {section_idx}: 页面宽度 {expected_width}cm vs {page_size['width_cm']:.2f}cm")
                if abs(page_size['height_cm'] - expected_height) > 0.1:
                    errors.append(f"节 {section_idx}: 页面高度 {expected_height}cm vs {page_size['height_cm']:.2f}cm")
            
            margins = utils.get_page_margins(section)
            
            if "top_margin_cm" in conditions:
                expected = conditions["top_margin_cm"]
                if abs(margins['top_cm'] - expected) > 0.1:
                    errors.append(f"节 {section_idx}: 上边距 {expected}cm vs {margins['top_cm']:.2f}cm")
            
            if "bottom_margin_cm" in conditions:
                expected = conditions["bottom_margin_cm"]
                if abs(margins['bottom_cm'] - expected) > 0.1:
                    errors.append(f"节 {section_idx}: 下边距 {expected}cm vs {margins['bottom_cm']:.2f}cm")
            
            if "left_margin_cm" in conditions:
                expected = conditions["left_margin_cm"]
                if abs(margins['left_cm'] - expected) > 0.1:
                    errors.append(f"节 {section_idx}: 左边距 {expected}cm vs {margins['left_cm']:.2f}cm")
            
            if "right_margin_cm" in conditions:
                expected = conditions["right_margin_cm"]
                if abs(margins['right_cm'] - expected) > 0.1:
                    errors.append(f"节 {section_idx}: 右边距 {expected}cm vs {margins['right_cm']:.2f}cm")
        
        if conditions.get("property") == "header_exists":
            expected = conditions.get("expected", True)
            zones = conditions.get("zones", [])
            has_header = False
            
            if self.doc.sections:
                section = self.doc.sections[0]
                if hasattr(section, 'header') and section.header:
                    has_header = True
            
            if has_header != expected:
                errors.append(f"页眉存在性检查: 预期 {expected}, 实际 {has_header}")
        
        if errors:
            # 使用规则中的 error_message（人类可读的格式要求）
            error_msg = rule.get('error_message', f"发现 {len(errors)} 处全局属性不符")
            
            # 添加当前检测到的实际值作为补充信息
            detail_msg = f"\n当前检测到: {'; '.join(errors[:3])}"
            if len(errors) > 3:
                detail_msg += f" ... 等{len(errors)}处"
            
            full_message = error_msg + detail_msg
            
            return CheckIssue(
                rule_id=rule_id,
                check_type="global_property",
                result=CheckResult.FAIL.value,
                message=full_message,
                location={"errors": errors[:5], "section_indices": list(range(len(self.doc.sections)))},
                severity="error"
            )
        
        return CheckIssue(
            rule_id=rule_id,
            check_type="global_property",
            result=CheckResult.PASS.value,
            message="全局属性检查通过",
            severity="info"
        )
