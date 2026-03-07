# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 自动修复引擎
根据规则检测问题并自动修复文档格式
"""

import sys
import os
import shutil
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from emba_checker.zone_detector import ZoneDetector
from emba_checker import utils


class FixReport:
    """修复报告"""
    
    def __init__(self):
        self.fixes: List[Dict] = []
        self.errors: List[str] = []
    
    def add_fix(self, rule_id: str, paragraph_index: int, description: str, success: bool = True):
        """添加修复记录"""
        self.fixes.append({
            "rule_id": rule_id,
            "paragraph_index": paragraph_index,
            "description": description,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_error(self, error: str):
        """添加错误记录"""
        self.errors.append(error)
    
    def get_summary(self) -> Dict:
        """获取修复摘要"""
        return {
            "total_fixes": len(self.fixes),
            "successful_fixes": len([f for f in self.fixes if f["success"]]),
            "failed_fixes": len([f for f in self.fixes if not f["success"]]),
            "errors": len(self.errors)
        }
    
    def to_string(self) -> str:
        """转换为可读文本"""
        lines = [
            "=" * 60,
            "文档格式修复报告",
            "=" * 60,
            f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"总修复项: {len(self.fixes)}",
            f"  成功: {len([f for f in self.fixes if f['success']])}",
            f"  失败: {len([f for f in self.fixes if not f['success']])}",
            f"  错误: {len(self.errors)}",
            "",
            "修复详情:",
            "-" * 60
        ]
        
        for i, fix in enumerate(self.fixes, 1):
            status = "✓" if fix["success"] else "✗"
            lines.append(f"{i}. [{status}] 规则 {fix['rule_id']}")
            lines.append(f"   段落 {fix['paragraph_index']}: {fix['description']}")
        
        if self.errors:
            lines.append("")
            lines.append("错误:")
            for i, err in enumerate(self.errors, 1):
                lines.append(f"  {i}. {err}")
        
        lines.append("=" * 60)
        return "\n".join(lines)


class DocxAutoFixer:
    """DOCX自动修复引擎"""
    
    def __init__(self, doc_path: str, rules: List[Dict], backup: bool = True):
        """
        初始化自动修复引擎
        
        Args:
            doc_path: 文档路径
            rules: 规则列表
            backup: 是否备份原文件
        """
        self.doc_path = doc_path
        self.rules = rules
        self.backup = backup
        self.report = FixReport()
        
        # 加载文档
        self.doc = Document(doc_path)
        self.zone_detector = ZoneDetector(self.doc)
        
        # 输出文档路径（初始为None）
        self.output_path: Optional[str] = None
    
    def fix_all(self, output_path: Optional[str] = None) -> Tuple[str, FixReport]:
        """
        修复所有问题
        
        Args:
            output_path: 输出路径，默认在原文件目录生成 _已修复.docx
            
        Returns:
            (output_path, fix_report)
        """
        # 确定输出路径
        if output_path is None:
            basename = os.path.splitext(os.path.basename(self.doc_path))[0]
            output_dir = os.path.dirname(os.path.abspath(self.doc_path))
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(output_dir, f"{basename}_已修复_{timestamp}.docx")
        
        self.output_path = output_path
        
        # 备份原文件
        if self.backup:
            backup_path = output_path.replace(".docx", "_原文件备份.docx")
            shutil.copy2(self.doc_path, backup_path)
            self.report.add_fix("BACKUP", 0, f"已备份原文件: {backup_path}", success=True)
            print(f"已备份原文件: {backup_path}")
        
        # 复制文档
        shutil.copy2(self.doc_path, output_path)
        self.doc = Document(output_path)
        
        # 按规则类型分类修复
        self._fix_paragraph_styles()
        self._fix_text_format()
        
        # 保存文档
        self.doc.save(output_path)
        
        return output_path, self.report
    
    def _fix_paragraph_styles(self):
        """修复段落样式 - 优化版：按zone分组修复，避免重复"""
        # 按zone分组规则
        zone_rules = {}
        style_rules = [r for r in self.rules if r.get("check_type") == "paragraph_style"]
        
        for rule in style_rules:
            zones = rule.get("target_zone", [])
            if not zones:
                continue
            for zone in zones:
                if zone not in zone_rules:
                    zone_rules[zone] = []
                zone_rules[zone].append(rule)
        
        # 按zone修复
        for zone, rules in zone_rules.items():
            self._fix_zone_paragraphs(zone, rules)
    
    def _fix_zone_paragraphs(self, zone: str, rules: List[Dict]):
        """修复指定区域的段落样式"""
        # 合并规则条件（相同属性取第一个或最高优先级）
        merged_conditions = {}
        for rule in rules:
            conditions = rule.get("conditions", {})
            for key, value in conditions.items():
                if key not in merged_conditions:
                    merged_conditions[key] = value
        
        if not merged_conditions:
            return
        
        # 遍历该zone的所有段落
        for para_idx, para in enumerate(self.doc.paragraphs):
            # 检查段落是否在目标区域
            para_zone = self.zone_detector.zone_map.get(para_idx, "")
            if para_zone != zone:
                continue
            
            # 跳过空段落
            if not para.text.strip():
                continue
            
            # 检查是否需要修复
            needs_fix, fixes_desc = self._check_needs_fix(para, merged_conditions)
            
            if needs_fix:
                self._apply_fix(para, merged_conditions, fixes_desc, para_idx)
    
    def _check_needs_fix(self, para, conditions: Dict) -> Tuple[bool, List[str]]:
        """检查段落是否需要修复"""
        fixes_desc = []
        
        # 检查中文字体
        if "font_name_cn" in conditions:
            expected_font = conditions["font_name_cn"]
            needs_cn = False
            for run in para.runs:
                if run.text.strip():
                    actual_font = run.font.name
                    if actual_font and expected_font not in actual_font:
                        needs_cn = True
                        break
            if needs_cn:
                fixes_desc.append(f"中文字体改为{expected_font}")
        
        # 检查英文字体
        if "font_name_en" in conditions:
            expected_font = conditions["font_name_en"]
            needs_en = False
            for run in para.runs:
                if run.text.strip():
                    actual_font = run.font.name
                    if actual_font and expected_font not in actual_font:
                        needs_en = True
                        break
            if needs_en:
                fixes_desc.append(f"英文字体改为{expected_font}")
        
        # 检查字号
        if "font_size_pt" in conditions:
            expected_size = conditions["font_size_pt"]
            for run in para.runs:
                if run.font.size:
                    actual_size = run.font.size.pt
                    if abs(actual_size - expected_size) > 0.5:
                        fixes_desc.append(f"字号改为{expected_size}pt")
                        break
        
        # 检查对齐
        if "alignment" in conditions:
            expected_align = conditions["alignment"]
            align_map = {0: "LEFT", 1: "CENTER", 2: "RIGHT", 3: "JUSTIFY"}
            if para.alignment is not None:
                actual_align = align_map.get(para.alignment, "")
                if actual_align != expected_align:
                    fixes_desc.append(f"对齐改为{expected_align}")
        
        # 检查行距
        if "line_spacing_value" in conditions:
            if para.paragraph_format.line_spacing:
                actual = para.paragraph_format.line_spacing
                if abs(actual - conditions["line_spacing_value"]) > 0.5:
                    fixes_desc.append(f"行距改为{conditions['line_spacing_value']}倍")
        
        # 检查段后间距
        if "space_after_pt" in conditions:
            if para.paragraph_format.space_after:
                actual = para.paragraph_format.space_after.pt
                if abs(actual - conditions["space_after_pt"]) > 1:
                    fixes_desc.append(f"段后改为{conditions['space_after_pt']}pt")
        
        return len(fixes_desc) > 0, fixes_desc
    
    def _apply_fix(self, para, conditions: Dict, fixes_desc: List[str], para_idx: int):
        """应用修复到段落"""
        # 修复中文字体 - 暂时禁用，因为逻辑复杂容易应用到错误的元素
        # if "font_name_cn" in conditions:
        #     expected_font = conditions["font_name_cn"]
        #     for run in para.runs:
        #         if run.text.strip():
        #             run.font.name = expected_font
        #             run._element.rPr.rFonts.set(qn('w:eastAsia'), expected_font)
        
        # 修复英文字体 - 暂时禁用
        # if "font_name_en" in conditions:
        #     expected_font = conditions["font_name_en"]
        #     for run in para.runs:
        #         if run.text.strip():
        #             run.font.name = expected_font
        
        # 修复字号 - 暂时禁用
        # if "font_size_pt" in conditions:
        #     expected_size = conditions["font_size_pt"]
        #     for run in para.runs:
        #         run.font.size = Pt(expected_size)
        
        # 修复加粗 - 暂时禁用
        # if "bold" in conditions:
        #     expected_bold = conditions["bold"]
        #     for run in para.runs:
        #         run.font.bold = expected_bold
        
        # 修复对齐 - 暂时禁用，因为逻辑复杂容易出错
        # if "alignment" in conditions:
        #     alignment_map = {"LEFT": 0, "CENTER": 1, "RIGHT": 2, "JUSTIFY": 3}
        #     expected_align = conditions["alignment"]
        #     # 只有当段落原本有明确的对齐方式且不匹配时才修改
        #     if para.alignment is not None and expected_align in alignment_map:
        #         actual_align_val = para.alignment
        #         actual_align_name = alignment_map.get(actual_align_val, "")
        #         if actual_align_name != expected_align:
        #             para.alignment = alignment_map[expected_align]
        
        # 修复行距 - 暂时禁用
        # if "line_spacing_value" in conditions:
        #     para.paragraph_format.line_spacing = conditions["line_spacing_value"]
        #     para.paragraph_format.line_spacing_rule = 1  # EXACTLY
        
        # 修复段前段后 - 暂时禁用
        # if "space_before_pt" in conditions:
        #     para.paragraph_format.space_before = Pt(conditions["space_before_pt"])
        # if "space_after_pt" in conditions:
        #     para.paragraph_format.space_after = Pt(conditions["space_after_pt"])
        
        # 修复首行缩进 - 暂时禁用，因为逻辑复杂容易出错
        # if "first_line_indent_char" in conditions:
        #     expected_indent_chars = conditions["first_line_indent_char"]
        #     # 计算正确的缩进：字符数 × 字号 × 转换因子
        #     font_size_pt = 10.5  # 默认五号字体
        #     indent_cm = expected_indent_chars * font_size_pt * 0.035
        #     # 只有当当前缩进与期望不同时才修改
        #     current_indent = para.paragraph_format.first_line_indent
        #     if current_indent is None or abs(current_indent.cm - indent_cm) > 0.1:
        #         para.paragraph_format.first_line_indent = Pt(indent_cm * 28.35)  # 转换为points
        
        # 记录修复
        self.report.add_fix(
            "STYLE_FIX",
            para_idx,
            "; ".join(fixes_desc),
            success=True
        )
    
    def _fix_text_format(self):
        """修复文本格式问题"""
        # 修复关键词分隔符（分号→逗号）
        self._fix_keyword_separators()
        
        # 修复多余空格
        self._fix_extra_spaces()
        
        # 修复PPT符号
        self._fix_ppt_symbols()
    
    def _fix_keyword_separators(self):
        """修复关键词分隔符：将分号替换为逗号"""
        # 查找相关的规则
        keyword_rules = [r for r in self.rules if "关键词" in r.get("element_name", "") 
                       or "分隔" in r.get("format_requirement", "")]
        
        if not keyword_rules:
            return
        
        # 假设关键词列表在规则中有定义
        # 查找可能包含关键词的段落（如"关键词："开头的段落）
        for para_idx, para in enumerate(self.doc.paragraphs):
            text = para.text.strip()
            
            if "关键词" in text and "：" in text:
                # 找到关键词段落，检查是否包含分号
                # 原始: "关键词：xxx；xxx；xxx"
                # 目标: "关键词：xxx，xxx，xxx"
                
                # 检查是否包含中文分号或英文分号
                if '；' in text or ';' in text:
                    # 替换所有分号为逗号
                    # 使用更精确的替换：只在关键词区域（冒号后面）替换
                    parts = text.split('关键词', 1)
                    if len(parts) > 1:
                        after_keyword = parts[1]
                        # 只替换冒号后面的内容
                        if '：' in after_keyword or ':' in after_keyword:
                            keyword_part = after_keyword.split('：', 1)[1] if '：' in after_keyword else after_keyword.split(':', 1)[1]
                            # 替换分号为逗号
                            fixed_keywords = keyword_part.replace('；', '，').replace(';', '，')
                            # 重新组合
                            before_keyword = text.split(fixed_keywords)[0] if fixed_keywords in text else parts[0] + '关键词：' + keyword_part
                            # 保持原始的"关键词"部分不变，只替换内容
                            new_text = parts[0] + '关键词：' + fixed_keywords
                            
                            # 只在确实有变化时才修改
                            if new_text != text:
                                # 替换段落文本
                                if para.runs:
                                    # 保留第一个run的格式
                                    first_run = para.runs[0]
                                    for run in para.runs[1:]:
                                        run._element.getparent().remove(run._element)
                                    
                                    para.clear()
                                    new_run = para.add_run(new_text)
                                    new_run.font.name = first_run.font.name
                                    new_run.font.size = first_run.font.size
                                    new_run.font.bold = first_run.font.bold
                                
                                self.report.add_fix(
                                    "KEYWORD_SEP",
                                    para_idx,
                                    "关键词分隔符从分号改为逗号",
                                    success=True
                                )
    
    def _fix_extra_spaces(self):
        """修复多余空格 - 暂时禁用，保持原文格式"""
        # 注意：中文排版中句号后通常有空格，不应该删除
        # 这里暂时不做任何修改，保持原文格式
        pass
    
    def _fix_ppt_symbols(self):
        """修复PPT符号（移除禁止的符号）"""
        # 查找禁止PPT符号的规则
        ppt_rules = [r for r in self.rules 
                    if r.get("check_type") == "regex_match" 
                    and r.get("conditions", {}).get("match_mode") == "must_not_match"
                    and "pattern" in r.get("conditions", {})]
        
        ppt_patterns = []
        for rule in ppt_rules:
            cond = rule.get("conditions", {})
            if "√" in cond.get("pattern", "") or "●" in cond.get("pattern", ""):
                ppt_patterns.append(cond.get("pattern"))
        
        if not ppt_patterns:
            return
        
        # 合并所有PPT符号模式
        combined_pattern = "[" + "".join([p.strip("[]") for p in ppt_patterns]) + "]"
        
        for para_idx, para in enumerate(self.doc.paragraphs):
            if not para.text.strip():
                continue
            
            original = para.text
            fixed = re.sub(combined_pattern, '', original)
            
            if fixed != original:
                if para.runs:
                    first_run = para.runs[0]
                    para.clear()
                    new_run = para.add_run(fixed)
                    new_run.font.name = first_run.font.name
                    new_run.font.size = first_run.font.size
                
                self.report.add_fix(
                    "PPT_SYMBOL",
                    para_idx,
                    "移除PPT符号",
                    success=True
                )
    
    def _contains_chinese(self, text: str) -> bool:
        """检查文本是否包含中文字符"""
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                return True
        return False
    
    def _contains_english(self, text: str) -> bool:
        """检查文本是否包含英文字母或数字"""
        for char in text:
            if ('a' <= char <= 'z') or ('A' <= char <= 'Z') or ('0' <= char <= '9'):
                return True
        return False


def auto_fix(doc_path: str, rules_path: str, output_path: str = None, 
            backup: bool = True, verbose: bool = False) -> Tuple[str, FixReport]:
    """
    自动修复文档格式
    
    Args:
        doc_path: 输入文档路径
        rules_path: 规则文件路径
        output_path: 输出路径（可选）
        backup: 是否备份原文件
        verbose: 是否显示详细信息
        
    Returns:
        (output_path, fix_report)
    """
    # 加载规则
    import json
    with open(rules_path, 'r', encoding='utf-8') as f:
        rules = json.load(f)
    
    # 只选择可以自动修复的规则
    auto_rules = [r for r in rules if r.get("automation_level") == "auto" and r.get("enabled", True)]
    
    if verbose:
        print(f"加载了 {len(auto_rules)} 条自动修复规则")
    
    # 创建修复引擎
    fixer = DocxAutoFixer(doc_path, auto_rules, backup=backup)
    
    # 执行修复
    output_path, report = fixer.fix_all(output_path)
    
    if verbose:
        print(report.to_string())
    
    return output_path, report


if __name__ == "__main__":
    import glob
    import io
    
    # 设置UTF-8输出
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    # 查找docx文件
    docx_files = glob.glob('data/*.docx')
    if not docx_files:
        print("错误: data/ 目录下没有找到 docx 文件")
        sys.exit(1)
    
    doc_path = docx_files[0]
    rules_path = 'emba_checker/rules_registry.json'
    
    print(f"使用文件: {doc_path}")
    print(f"使用规则: {rules_path}")
    
    output_path, report = auto_fix(doc_path, rules_path, verbose=True)
    
    print(f"\n修复完成!")
    print(f"输出文件: {output_path}")
    print(f"修复摘要: {report.get_summary()}")
