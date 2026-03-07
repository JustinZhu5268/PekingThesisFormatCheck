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
                # 忽略 NONE 或 None 的情况（表示使用默认对齐）
                if actual_alignment and actual_alignment != 'NONE':
                    # 如果期望是 JUSTIFY，但文档是 DISTRIBUTE，也视为通过（Word中两者效果相似）
                    if expected_alignment == 'JUSTIFY' and actual_alignment in ['JUSTIFY', 'DISTRIBUTE']:
                        pass  # 视为通过
                    elif actual_alignment != expected_alignment:
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
            # 使用规则中的 error_message（人类可读的格式要求）
            error_msg = rule.get('error_message', f"发现 {len(errors)} 处样式不符")
            
            # 生成具体修改建议
            suggestions = _generate_suggestions(rule, errors)
            
            # 添加当前检测到的实际值作为补充信息
            detail_msg = f"\n当前检测到: {'; '.join(errors[:3])}"
            if len(errors) > 3:
                detail_msg += f" ... 等{len(errors)}处"
            
            full_message = error_msg + detail_msg + "\n" + suggestions
            
            return CheckIssue(
                rule_id=rule_id,
                check_type="paragraph_style",
                result=CheckResult.FAIL.value,
                message=full_message,
                location={"zones": zones, "errors": errors[:5], "paragraph_indices": [i for i, p in paragraphs]},
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


def _generate_suggestions(rule: dict, errors: list) -> str:
    """根据规则和错误生成具体的修改建议"""
    format_req = rule.get('format_requirement', '')
    rule_id = rule.get('rule_id', '')
    
    suggestions = []
    
    # 字体建议
    if '黑体' in format_req:
        suggestions.append("► 字体应改为: 黑体")
    if '宋体' in format_req:
        suggestions.append("► 字体应改为: 宋体")
    if '仿宋' in format_req:
        suggestions.append("► 字体应改为: 仿宋")
    if '楷体' in format_req:
        suggestions.append("► 字体应改为: 楷体")
    if 'Times New Roman' in format_req or 'Times' in format_req:
        suggestions.append("► 字体应改为: Times New Roman")
    
    # 字号建议
    if '一号' in format_req or '26pt' in str(format_req):
        suggestions.append("► 字号应改为: 一号(26pt)")
    if '二号' in format_req or '22pt' in str(format_req):
        suggestions.append("► 字号应改为: 二号(22pt)")
    if '三号' in format_req or '16pt' in str(format_req):
        suggestions.append("► 字号应改为: 三号(16pt)")
    if '小三' in format_req or '15pt' in str(format_req):
        suggestions.append("► 字号应改为: 小三(15pt)")
    if '四号' in format_req or '14pt' in str(format_req):
        suggestions.append("► 字号应改为: 四号(14pt)")
    if '小四' in format_req or '12pt' in str(format_req):
        suggestions.append("► 字号应改为: 小四(12pt)")
    if '五号' in format_req or '10.5pt' in str(format_req):
        suggestions.append("► 字号应改为: 五号(10.5pt)")
    
    # 对齐建议
    if '居中' in format_req:
        suggestions.append("► 对齐方式应改为: 居中")
    if '两端对齐' in format_req or 'JUSTIFY' in format_req:
        suggestions.append("► 对齐方式应改为: 两端对齐")
    if '左对齐' in format_req:
        suggestions.append("► 对齐方式应改为: 左对齐")
    
    # 加粗建议
    if '加粗' in format_req:
        suggestions.append("► 需要设置: 加粗")
    if '不加粗' in format_req or '不加粗' in format_req:
        suggestions.append("► 需要取消: 加粗")
    
    # 缩进建议
    if '首行缩进' in format_req or '2字符' in format_req:
        suggestions.append("► 首行缩进应设置为: 2字符(0.74cm)")
    
    # 行距建议
    if '倍行距' in format_req:
        import re
        match = re.search(r'(\d+\.?\d*)\s*倍行距', format_req)
        if match:
            suggestions.append(f"► 行距应设置为: {match.group(1)}倍行距")
        else:
            suggestions.append("► 行距应设置为: 1.25倍行距")
    
    # 关键词分隔符建议
    if '关键词' in format_req:
        if '逗号' in format_req or '，' in format_req:
            suggestions.append("► 关键词分隔符应使用: 中文逗号'，' (不是分号';')")
    
    if not suggestions:
        suggestions.append(f"► 请参照格式要求: {format_req[:60]}...")
    
    return '\n'.join(suggestions)
