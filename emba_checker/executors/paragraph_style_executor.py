# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 段落样式执行器
"""

import sys
import os
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_executor import BaseExecutor, CheckIssue, CheckResult
import utils


class ParagraphStyleExecutor(BaseExecutor):
    """段落样式执行器"""
    
    def check(self, rule: Dict) -> CheckIssue:
        conditions = rule.get("conditions", {})
        zones = rule.get("target_zone", [])
        rule_id = rule.get("rule_id", "")
        
        # 如果条件为空，返回 SKIP
        if not conditions:
            return CheckIssue(
                rule_id=rule_id,
                check_type="paragraph_style",
                result=CheckResult.SKIP.value,
                message="规则条件未配置，跳过检查",
                severity="info"
            )
        
        paragraphs = self._get_paragraphs_in_zones(zones)
        
        if not paragraphs:
            return CheckIssue(
                rule_id=rule_id,
                check_type="paragraph_style",
                result=CheckResult.SKIP.value,
                message=f"在指定区域 {zones} 中未找到段落",
                severity="info"
            )
        
        errors = []
        
        # 中文字体检查
        if "font_name_cn" in conditions:
            expected_font = conditions["font_name_cn"]
            for idx, para in paragraphs:
                for run in para.runs:
                    actual_font = utils.get_east_asia_font(run)
                    if actual_font and expected_font not in actual_font:
                        errors.append(f"段落 {idx}: 字体 {expected_font} vs {actual_font}")
        
        # 字号检查
        if "font_size_pt" in conditions:
            expected_size = conditions["font_size_pt"]
            for idx, para in paragraphs:
                for run in para.runs:
                    actual_size = utils.get_font_size(run)
                    if actual_size and abs(actual_size - expected_size) > 0.5:
                        errors.append(f"段落 {idx}: 字号 {expected_size}pt vs {actual_size}pt")
        
        # 加粗检查
        if "bold" in conditions:
            expected_bold = conditions["bold"]
            for idx, para in paragraphs:
                for run in para.runs:
                    actual_bold = utils.get_font_bold(run)
                    if actual_bold is not None and actual_bold != expected_bold:
                        errors.append(f"段落 {idx}: 加粗 {expected_bold} vs {actual_bold}")
        
        # 对齐检查
        if "alignment" in conditions:
            expected_alignment = conditions["alignment"]
            for idx, para in paragraphs:
                actual_alignment = utils.get_paragraph_alignment(para)
                if actual_alignment and actual_alignment != expected_alignment:
                    errors.append(f"段落 {idx}: 对齐 {expected_alignment} vs {actual_alignment}")
        
        # 首行缩进检查
        if "first_line_indent_char" in conditions:
            expected_indent = conditions["first_line_indent_char"]
            for idx, para in paragraphs:
                actual_indent = utils.get_first_line_indent(para)
                if actual_indent is not None and abs(actual_indent - expected_indent) > 0.2:
                    errors.append(f"段落 {idx}: 首行缩进 {expected_indent}字符 vs {actual_indent}字符")
        
        # 行距检查
        if "line_spacing_value" in conditions:
            expected_spacing = conditions["line_spacing_value"]
            for idx, para in paragraphs:
                spacing_info = utils.get_line_spacing(para)
                if spacing_info and spacing_info.get("value"):
                    actual_spacing = spacing_info.get("value")
                    if abs(actual_spacing - expected_spacing) > 0.2:
                        errors.append(f"段落 {idx}: 行距 {expected_spacing} vs {actual_spacing}")
        
        # 段前段后检查
        if "space_before_pt" in conditions:
            expected_space = conditions["space_before_pt"]
            for idx, para in paragraphs:
                actual_space = utils.get_space_before(para)
                if actual_space is not None and abs(actual_space - expected_space) > 1:
                    errors.append(f"段落 {idx}: 段前 {expected_space}pt vs {actual_space}pt")
        
        if "space_after_pt" in conditions:
            expected_space = conditions["space_after_pt"]
            for idx, para in paragraphs:
                actual_space = utils.get_space_after(para)
                if actual_space is not None and abs(actual_space - expected_space) > 1:
                    errors.append(f"段落 {idx}: 段后 {expected_space}pt vs {actual_space}pt")
        
        # 样式名称检查
        if "style_name_contains" in conditions:
            style_keyword = conditions["style_name_contains"]
            for idx, para in paragraphs:
                if para.style and para.style.name:
                    if style_keyword not in para.style.name:
                        errors.append(f"段落 {idx}: 样式应包含 '{style_keyword}'")
        
        if errors:
            return CheckIssue(
                rule_id=rule_id,
                check_type="paragraph_style",
                result=CheckResult.FAIL.value,
                message=f"发现 {len(errors)} 处样式不符: {'; '.join(errors[:3])}",
                location={"zones": zones, "errors": errors[:5]},
                severity="error"
            )
        
        return CheckIssue(
            rule_id=rule_id,
            check_type="paragraph_style",
            result=CheckResult.PASS.value,
            message=f"段落样式检查通过",
            location={"zones": zones},
            severity="info"
        )
