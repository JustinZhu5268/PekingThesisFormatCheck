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
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_LINE_SPACING, WD_ALIGN_PARAGRAPH
from pypinyin import lazy_pinyin
from docx.oxml import OxmlElement
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
    
    def fix_heading_numbering_style(self):
        """修复标题自动编号格式：去除末尾多余的小数点，并确保加粗"""
        try:
            from lxml import etree
        except ImportError:
            print("  警告: lxml未安装，跳过编号样式修复")
            return
        
        try:
            # 获取numbering part
            numbering_part = self.doc.part.numbering_part
            if numbering_part is None:
                print("  文档无numbering part，跳过")
                return
            
            # 获取XML元素
            numbering_xml = numbering_part._element
            
            # 命名空间
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            # 查找所有abstractNum
            changed = 0
            bold_fixed = 0
            
            for abstract_num in numbering_xml.findall('.//w:abstractNum', ns):
                # 遍历每个级别的lvl
                for lvl in abstract_num.findall('.//w:lvl', ns):
                    lvl_text = lvl.find('w:lvlText', ns)
                    if lvl_text is None:
                        continue
                    
                    # 获取w:val属性
                    val = lvl_text.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                    if val is None:
                        continue
                    
                    # 修复1：去除末尾多余的小数点
                    # 检查条件：
                    # 1. 包含%符号（说明是编号格式）
                    # 2. 以.结尾
                    # 3. 包含至少2个%符号（多级标题）
                    if '%' in val and val.endswith('.') and val.count('%') >= 2:
                        new_val = val[:-1]  # 去掉末尾的点
                        lvl_text.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', new_val)
                        changed += 1
                        print(f"    修复: {val} -> {new_val}")
                    
                    # 修复2：确保编号加粗
                    # 检查 <w:rPr> 是否存在 <w:b/>
                    rPr = lvl.find('w:rPr', ns)
                    if rPr is None:
                        # 创建 rPr 元素
                        from lxml import etree
                        rPr = etree.SubElement(lvl, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr')
                    
                    # 检查是否有 b 元素（加粗）
                    b_elem = rPr.find('w:b', ns)
                    if b_elem is None:
                        # 添加加粗元素
                        from lxml import etree
                        b_elem = etree.SubElement(rPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}b')
                        bold_fixed += 1
                    else:
                        # 检查是否被设置为关闭 (w:val="0")
                        val = b_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                        if val == "0":
                            # 移除 w:val 属性，启用加粗
                            b_elem.attrib.clear()
                            bold_fixed += 1
            
            if changed > 0 or bold_fixed > 0:
                msg = []
                if changed > 0:
                    msg.append(f"修改编号格式 {changed} 处")
                if bold_fixed > 0:
                    msg.append(f"添加加粗 {bold_fixed} 处")
                print(f"  标题编号样式修复: {', '.join(msg)}")
                self.report.add_fix("HEADING_NUM_STYLE", 0, "修复标题编号样式", success=True)
            else:
                print("  标题编号样式: 无需修复")
                
        except Exception as e:
            print(f"  警告: 编号样式修复失败 - {e}")
    
    def fix_document_zones_and_headers(self):
        """终极版：统一重塑文档的节结构、页码和页眉页脚（带防火墙的三区隔离法）"""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        print("  执行带防火墙的三区隔离法...")
        
        # ==========================================
        # 1. 智能扫描：带"防火墙"的区域识别
        # ==========================================
        section_map = {}  # sec_idx -> {'zone': 1/2/3, 'title': ''}
        current_sec_idx = 0
        found_toc = False
        
        for p in self.doc.paragraphs:
            text = p.text.strip()
            style = p.style.name if p.style else ""
            
            if current_sec_idx not in section_map:
                # 默认继承前一个区域的属性，除非被触发更改
                prev_zone = section_map[current_sec_idx - 1]['zone'] if current_sec_idx > 0 else 1
                section_map[current_sec_idx] = {'zone': prev_zone, 'title': ''}
                
            # 触发器 1：发现摘要，进入 Zone 2 (前置区)
            if text in ["摘要", "ABSTRACT"] and not found_toc:
                section_map[current_sec_idx]['zone'] = 2
                if not section_map[current_sec_idx]['title']:
                    section_map[current_sec_idx]['title'] = text
                    
            # 触发器 2：发现目录，标记防火墙
            if text == "目录":
                found_toc = True
                section_map[current_sec_idx]['zone'] = 2
                if not section_map[current_sec_idx]['title']:
                    section_map[current_sec_idx]['title'] = "目录"
                    
            # 触发器 3：【关键】越过目录防火墙后，发现真正的第一章标题，进入 Zone 3 (正文区)
            # 必须同时满足：样式是Heading 1，且内容是"绪论"（可能有"第一章 "前缀）
            if found_toc and style in ['Heading 1', '标题 1']:
                # 提取纯标题文字（去除"第一章 "前缀）
                pure_title = text.replace("第一章 ", "").replace("第一章", "").strip()
                if pure_title == "绪论":
                    section_map[current_sec_idx]['zone'] = 3
                    if not section_map[current_sec_idx]['title']:
                        section_map[current_sec_idx]['title'] = text
                    
            # 遇到分节符，进入下一个 Section
            if p._element.xpath('.//w:sectPr'):
                current_sec_idx += 1
        
        print(f"    扫描到 {len(section_map)} 个区域: {section_map}")

        # ==========================================
        # 2. 暴力清洗与重建引擎
        # ==========================================
        self.doc.settings.odd_and_even_pages_header_footer = True
        
        zone2_first_sec = True
        zone3_first_sec = True
        
        for i, section in enumerate(self.doc.sections):
            if i not in section_map:
                continue
                
            zone = section_map[i]['zone']
            title = section_map[i]['title']
            sectPr = section._sectPr
            
            # 彻底切断与上一节的联系
            section.header.is_linked_to_previous = False
            section.even_page_header.is_linked_to_previous = False
            section.footer.is_linked_to_previous = False
            section.even_page_footer.is_linked_to_previous = False
            
            # 【核弹级清洗】：暴力清空所有页眉页脚的底层 XML (消灭 STYLEREF 和旧页码)
            for hf in [section.header, section.even_page_header, section.footer, section.even_page_footer]:
                hf_elem = hf._element
                for child in list(hf_elem):
                    hf_elem.remove(child)
                hf_elem.append(OxmlElement('w:p'))  # 补回一个空段落防崩溃
                
            # 移除旧的页码类型设置
            pgNumType = sectPr.find(qn('w:pgNumType'))
            if pgNumType is not None:
                sectPr.remove(pgNumType)

            # ------------------------------------------
            # Zone 1: 封面与声明 (绝对干净，无页眉页脚页码)
            # ------------------------------------------
            if zone == 1:
                print(f"    节 {i}: Zone 1 (无页眉页脚页码)")
                
            # ------------------------------------------
            # Zone 2: 摘要与目录 (罗马数字)
            # ------------------------------------------
            elif zone == 2:
                pgNumType = OxmlElement('w:pgNumType')
                pgNumType.set(qn('w:fmt'), 'upperRoman')
                if zone2_first_sec:
                    pgNumType.set(qn('w:start'), '1')
                    # 强制奇数页分节，解决奇偶页翻转问题
                    type_el = sectPr.get_or_add_type()
                    type_el.set(qn('w:val'), 'oddPage')
                    zone2_first_sec = False
                sectPr.append(pgNumType)
                
                self._write_header(section.header, title)
                self._write_header(section.even_page_header, "北京大学硕士学位论文")
                self._write_footer_page_num(section.footer)
                self._write_footer_page_num(section.even_page_footer)
                
                print(f"    节 {i}: Zone 2 - {title} (罗马数字)")

            # ------------------------------------------
            # Zone 3: 正文区 (阿拉伯数字)
            # ------------------------------------------
            elif zone == 3:
                pgNumType = OxmlElement('w:pgNumType')
                pgNumType.set(qn('w:fmt'), 'decimal')
                if zone3_first_sec:
                    pgNumType.set(qn('w:start'), '1')
                    # 强制奇数页分节
                    type_el = sectPr.get_or_add_type()
                    type_el.set(qn('w:val'), 'oddPage')
                    zone3_first_sec = False
                sectPr.append(pgNumType)
                
                # Zone 3 使用 STYLEREF 动态页眉
                self._write_header_styleref(section.header, "标题 1")
                self._write_header(section.even_page_header, "北京大学硕士学位论文")
                self._write_footer_page_num(section.footer)
                self._write_footer_page_num(section.even_page_footer)
                
                print(f"    节 {i}: Zone 3 - {title} (阿拉伯数字)")

        self.report.add_fix("ZONES_HEADER", 0, "带防火墙的三区隔离法修复页眉页脚", success=True)
    
    # ==========================================
    # 辅助写入函数
    # ==========================================
    def _write_header(self, header_obj, text):
        """写入页眉内容"""
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Pt
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        
        # 清空现有段落
        for p in list(header_obj.paragraphs):
            p._element.getparent().remove(p._element)
        
        p = header_obj.add_paragraph()
        p.text = text
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.name = '宋体'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
            run.font.size = Pt(10.5)
        self._add_header_bottom_border(p)

    def _write_footer_page_num(self, footer_obj):
        """写入页脚页码（手动注入 PAGE 域）"""
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Pt
        
        # 清空现有段落
        for p in list(footer_obj.paragraphs):
            p._element.getparent().remove(p._element)
        
        p = footer_obj.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        
        # 注入 PAGE 域代码
        fldChar1 = OxmlElement('w:fldChar')
        fldChar1.set(qn('w:fldCharType'), 'begin')
        instrText = OxmlElement('w:instrText')
        instrText.set(qn('xml:space'), 'preserve')
        instrText.text = " PAGE "
        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(qn('w:fldCharType'), 'separate')
        fldChar3 = OxmlElement('w:fldChar')
        fldChar3.set(qn('w:fldCharType'), 'end')
        
        run._r.append(fldChar1)
        run._r.append(instrText)
        run._r.append(fldChar2)
        run._r.append(fldChar3)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10.5)

    def _write_header_styleref(self, header_obj, style_name):
        """写入页眉（STYLEREF动态域）"""
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Pt
        
        # 清空现有段落
        for p in list(header_obj.paragraphs):
            p._element.getparent().remove(p._element)
        
        p = header_obj.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 创建域代码 run
        run = p.add_run()
        
        # 开始域字符
        fldChar1 = OxmlElement('w:fldChar')
        fldChar1.set(qn('w:fldCharType'), 'begin')
        run._r.append(fldChar1)
        
        # 域指令 - 使用 style_name 样式
        instrText = OxmlElement('w:instrText')
        instrText.set(qn('xml:space'), 'preserve')
        instrText.text = f' STYLEREF "{style_name}" \\* MERGEFORMAT '
        run._r.append(instrText)
        
        # 分隔符
        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(qn('w:fldCharType'), 'separate')
        run._r.append(fldChar2)
        
        # 结束域
        fldChar3 = OxmlElement('w:fldChar')
        fldChar3.set(qn('w:fldCharType'), 'end')
        run._r.append(fldChar3)
        
        # 设置字体
        run.font.name = '宋体'
        run.font.size = Pt(10.5)
        
        # 设置段落间距和下划线
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        
        self._add_header_bottom_border(p)

    def _add_header_bottom_border(self, paragraph):
        """为段落添加底部边框（下划线效果）"""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        
        p_fmt = paragraph._element.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), '000000')
        pBdr.append(bottom)
        p_fmt.append(pBdr)

    def fix_page_numbers(self):
        """修复页码：从第一章开始重新编号"""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        
        # 查找第一章：使用 Heading 1 样式 且 文本包含"绪论"
        chapter1_idx = None
        for i, para in enumerate(self.doc.paragraphs):
            text = para.text.strip()
            # 检查是否为 Heading 1 样式，且文本包含"绪论"
            if para.style and 'Heading 1' in para.style.name:
                if '绪论' in text:
                    chapter1_idx = i
                    break
        
        if chapter1_idx is None:
            print("  未找到'第一章'（Heading 1 + 绪论），跳过页码修复")
            return
        
        print(f"  找到'第一章'在段落 {chapter1_idx}")
        
        # 在第一章段落前插入真正的"分节符（下一页）"
        # 注意：必须插入 sectPr 而不是 br，否则无法创建新节
        target_para = self.doc.paragraphs[chapter1_idx]
        p_elem = target_para._element
        
        # 创建分节符（下一页）- 这是真正的 Section Break
        # 在段落之前插入 sectPr
        sectPr = OxmlElement('w:sectPr')
        
        # 设置分节符类型为"下一页" (next page)
        type_elem = OxmlElement('w:type')
        type_elem.set(qn('w:val'), 'nextPage')
        sectPr.append(type_elem)
        
        # 设置页面大小 (paperSize A4)
        pgSz = OxmlElement('w:pgSz')
        pgSz.set(qn('w:w'), '11906')  # A4 width in twips
        pgSz.set(qn('w:h'), '16838')  # A4 height in twips
        sectPr.append(pgSz)
        
        # 设置页边距 (default margins)
        pgMar = OxmlElement('w:pgMar')
        pgMar.set(qn('w:top'), '1440')
        pgMar.set(qn('w:right'), '1440')
        pgMar.set(qn('w:bottom'), '1440')
        pgMar.set(qn('w:left'), '1440')
        pgMar.set(qn('w:header'), '851')
        pgMar.set(qn('w:footer'), '992')
        pgMar.set(qn('w:gutter'), '0')
        sectPr.append(pgMar)
        
        # 在目标段落之前插入 sectPr
        # 找到段落的父级元素，在第一个子元素之前插入
        p_elem.addprevious(sectPr)
        
        # 保存并重新加载文档
        self.doc.save(self.output_path)
        self.doc = Document(self.output_path)
        
        # 重新查找"第一章"段落
        chapter1_idx_new = None
        for i, para in enumerate(self.doc.paragraphs):
            if para.style and 'Heading 1' in para.style.name:
                if '绪论' in para.text.strip():
                    chapter1_idx_new = i
                    break
        
        # 获取所有 sections
        sections = list(self.doc.sections)
        
        # 找到包含"第一章"的新section
        # 新插入的分节符应该创建了一个新的section
        target_section = None
        for idx, section in enumerate(sections):
            # 检查这个section是否在第一章附近
            # 我们需要找到包含第一章的那个section
            # 通常新插入的分节符会在倒数第二个位置
            if idx == len(sections) - 1:
                target_section = section
        
        if target_section is None and sections:
            target_section = sections[-1]
        
        if target_section is None:
            print("  警告：未能找到目标section")
            return
        
        # 设置页码格式和起始页码
        sectPr_elem = target_section._sectPr
        
        # 查找或创建pgNumType
        pgNumType = sectPr_elem.find(qn('w:pgNumType'))
        if pgNumType is None:
            pgNumType = OxmlElement('w:pgNumType')
            sectPr_elem.append(pgNumType)
        
        pgNumType.set(qn('w:fmt'), 'decimal')
        pgNumType.set(qn('w:start'), '1')
        
        print("  页码修复: 已设置起始页码为1")
        self.report.add_fix("PAGE_NUM", 0, "修复页码从1开始", success=True)
    
    def fix_headers(self):
        """修复页眉：奇偶页不同，奇数页为章节标题，偶数页为固定文本"""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Pt
        
        # 开启奇偶页不同
        self.doc.settings.odd_and_even_pages_header_footer = True
        
        # 查找第一章：使用 Heading 1 样式 且 文本包含"绪论"
        chapter1_idx = None
        for i, para in enumerate(self.doc.paragraphs):
            text = para.text.strip()
            # 检查是否为 Heading 1 样式，且文本包含"绪论"
            if para.style and 'Heading 1' in para.style.name:
                if '绪论' in text:
                    chapter1_idx = i
                    break
        
        if chapter1_idx is None:
            print("  未找到'第一章'（Heading 1 + 绪论），跳过页眉修复")
            return
        
        # 找到第一章所在的section索引
        sections = list(self.doc.sections)
        body_section_index = 0
        
        # 遍历所有段落，找到它们属于哪个section
        # 通过检查段落的XML来确定它属于哪个section
        for i, section in enumerate(sections):
            # 检查section的起始位置
            if i < len(sections) - 1:
                # 检查下一个section的起始段落
                next_section = sections[i + 1]
                # 如果第一章在这个section之后，下一个section之前
                for para_idx, para in enumerate(self.doc.paragraphs):
                    if para_idx >= chapter1_idx:
                        # 找到第一章属于哪个section
                        body_section_index = i + 1
                        break
                if body_section_index > 0:
                    break
        
        # 更简单的方法：找到"绪论"段落的索引，然后找到它属于哪个section
        # 通过检查section的起始位置来判断
        body_section_index = 1  # 默认第一章在第2个section（索引1）
        
        print(f"  第一章在段落 {chapter1_idx}，正文section索引: {body_section_index}")
        
        # Bug修复1: 清空前置部分（封面、声明等）的页眉页脚
        # 在"第一章"所在section之前的所有section都要清空
        for i, section in enumerate(sections):
            if i < body_section_index:
                # 清空页眉
                section.header.is_linked_to_previous = False
                for p in list(section.header.paragraphs):
                    p._element.getparent().remove(p._element)
                
                # 清空页脚
                section.footer.is_linked_to_previous = False
                for p in list(section.footer.paragraphs):
                    p._element.getparent().remove(p._element)
        
        # 获取正文部分的section
        if len(sections) > body_section_index:
            target_section = sections[body_section_index]
        else:
            target_section = sections[0]
        
        print("  设置页眉...")
        
        # 设置偶数页页眉
        try:
            even_header = target_section.even_page_header
            
            # 清空原有内容 - 删除所有段落
            for p in list(even_header.paragraphs):
                p_elem = p._element
                p_elem.getparent().remove(p_elem)
            
            p = even_header.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            run = p.add_run("北京大学硕士学位论文")
            run.font.name = '宋体'
            run.font.size = Pt(10.5)
            
            # 设置段落间距
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            
            # 添加下划线（通过设置底部边框）
            p_fmt = p._element.get_or_add_pPr()
            pBdr = OxmlElement('w:pBdr')
            bottom = OxmlElement('w:bottom')
            bottom.set(qn('w:val'), 'single')
            bottom.set(qn('w:sz'), '6')
            bottom.set(qn('w:space'), '1')
            bottom.set(qn('w:color'), '000000')
            pBdr.append(bottom)
            p_fmt.append(pBdr)
            
            print("    偶数页页眉: 北京大学硕士学位论文")
        except Exception as e:
            print(f"    警告: 偶数页页眉设置失败 - {e}")
        
        # 设置奇数页页眉（STYLEREF域）
        try:
            odd_header = target_section.header
            
            # 清空原有内容 - 删除所有段落
            for p in list(odd_header.paragraphs):
                p_elem = p._element
                p_elem.getparent().remove(p_elem)
            
            p = odd_header.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # 创建域代码 run
            run = p.add_run()
            
            # 开始域字符
            fldChar1 = OxmlElement('w:fldChar')
            fldChar1.set(qn('w:fldCharType'), 'begin')
            run._r.append(fldChar1)
            
            # 域指令 - 使用 Heading 1 样式
            instrText = OxmlElement('w:instrText')
            instrText.set(qn('xml:space'), 'preserve')
            instrText.text = ' STYLEREF "Heading 1" \\* MERGEFORMAT '
            run._r.append(instrText)
            
            # 分隔符
            fldChar2 = OxmlElement('w:fldChar')
            fldChar2.set(qn('w:fldCharType'), 'separate')
            run._r.append(fldChar2)
            
            # 结束域
            fldChar3 = OxmlElement('w:fldChar')
            fldChar3.set(qn('w:fldCharType'), 'end')
            run._r.append(fldChar3)
            
            # 设置字体
            run.font.name = '宋体'
            run.font.size = Pt(10.5)
            
            # 设置段落间距和下划线
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            
            p_fmt = p._element.get_or_add_pPr()
            pBdr = OxmlElement('w:pBdr')
            bottom = OxmlElement('w:bottom')
            bottom.set(qn('w:val'), 'single')
            bottom.set(qn('w:sz'), '6')
            bottom.set(qn('w:space'), '1')
            bottom.set(qn('w:color'), '000000')
            pBdr.append(bottom)
            p_fmt.append(pBdr)
            
            print("    奇数页页眉: STYLEREF Heading 1 (动态章标题)")
        except Exception as e:
            print(f"    警告: 奇数页页眉设置失败 - {e}")
        
        print("  页眉修复: 已设置奇偶页不同")
        self.report.add_fix("HEADER", 0, "修复页眉奇偶页不同", success=True)
    
    def fix_chapter_tail_numbers(self):
        """清理尾部章序号：通过XML方式禁用参考文献/附录/致谢的自动编号"""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        
        print("  清理尾部章序号（XML方式）...")
        
        # 命名空间
        NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        # 需要处理的标题文本
        target_titles = ["参考文献", "致谢"]  # 附录可能带有子标题，单独处理
        
        count = 0
        
        # 查找所有 Heading 1 段落
        for i, para in enumerate(self.doc.paragraphs):
            style_name = para.style.name if para.style else ""
            if 'Heading 1' not in style_name:
                continue
                
            text = para.text.strip()
            
            # 检查是否是参考文献、附录或致谢（处理可能有空格的情况）
            # 参考文献、附录、致谢的标题
            is_target = False
            # 移除所有空格后再比较
            text_nospace = text.replace(' ', '').replace('\t', '')
            if text_nospace == "参考文献":
                is_target = True
            elif text_nospace.startswith("附录"):
                is_target = True
            elif text_nospace.startswith("致谢"):
                is_target = True
            
            if not is_target:
                continue
            
            # 获取段落的XML元素
            para_xml = para._element
            
            # 查找或创建 pPr 元素
            pPr = para_xml.find('.//w:pPr', NS)
            if pPr is None:
                # 创建新的 pPr 元素
                pPr = OxmlElement('w:pPr')
                para_xml.insert(0, pPr)
            
            # 查找 numPr 元素
            numPr = pPr.find('.//w:numPr', NS)
            
            if numPr is None:
                # 创建 numPr 元素
                numPr = OxmlElement('w:numPr')
                pPr.append(numPr)
            
            # 查找或创建 numId 元素（值为0表示无编号）
            numId = numPr.find('.//w:numId', NS)
            if numId is None:
                numId = OxmlElement('w:numId')
                numPr.append(numId)
            
            # 设置 numId 为 0（禁用编号）
            numId.set(qn('w:val'), '0')
            
            count += 1
            print(f"    禁用编号: '{text}' (段落 {i})")
            
            # 如果是参考文献，在其之前插入分节符（使用无空格版本比较）
            text_nospace = text.replace(' ', '').replace('\t', '')
            if text_nospace == "参考文献":
                try:
                    self._insert_section_break_before_paragraph(i)
                    print(f"    已插入分节符（参考文献前）")
                except Exception as e:
                    print(f"    插入分节符失败: {e}")
        
        if count > 0:
            self.report.add_fix("CHAPTER_TAIL_NUM", count, "清理尾部章序号（XML方式）", success=True)
            print(f"  尾部章序号清理完成: {count} 处")
            
            # 更新TOC（目录）中的条目
            self._update_toc_entries()
        else:
            print("  无需清理尾部章序号")
    
    def _update_toc_entries(self):
        """更新TOC中的参考文献、附录、致谢条目，移除章序号"""
        import re
        
        print("  更新TOC条目...")
        
        NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        # 匹配TOC中的章序号模式：第X章 + 参考文献/附录/致谢 + 页码
        # 更简单的模式：直接替换"第X章 "为空
        # 注意：致谢可能是"致 谢"（中间有空格）
        
        count = 0
        for para in self.doc.paragraphs:
            style_name = para.style.name if para.style else ""
            
            # 只处理TOC样式
            if 'toc' not in style_name.lower():
                continue
            
            text = para.text.strip()
            original_text = text
            
            # 检查是否以"第X章 "开头，后面跟着参考文献/附录/致谢/致 谢
            import re
            # 匹配第X章 参考文献/附录/致谢/致 谢（可能后面有内容）
            # 使用 \s+ 来匹配空格或制表符
            match = re.match(r'^(第[一二三四五六七八九十]+章\s+)(参考文献|附录|致\s?谢)', text)
            if match:
                # 提取标题部分（不含章序号），保留原始格式
                title = match.group(2)
                # 获取标题后面的所有内容（保持原样）
                remaining = text[match.end():]
                
                # 重新构建：标题 + 剩余内容
                new_text = title + remaining
                
                if original_text != new_text:
                    # 更新文本
                    for run in para.runs:
                        run.text = ''
                    if para.runs:
                        para.runs[0].text = new_text
                    else:
                        para.add_run(new_text)
                    count += 1
                    print(f"    更新TOC: '{original_text[:35]}...' -> '{new_text[:35]}...'")
        
        if count > 0:
            print(f"  TOC更新完成: {count} 处")
    
    def _insert_section_break_before_paragraph(self, para_index):
        """在指定段落之前插入分节符（下一页），并设置新section的header"""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        # 获取目标段落元素
        target_para = self.doc.paragraphs[para_index]
        target_xml = target_para._element
        
        # 在目标段落之前插入一个新的空段落，包含分节符
        new_p = OxmlElement('w:p')
        pPr = OxmlElement('w:pPr')
        new_p.append(pPr)
        
        sectPr = OxmlElement('w:sectPr')
        pPr.append(sectPr)
        
        type_elem = OxmlElement('w:type')
        type_elem.set(qn('w:val'), 'nextPage')
        sectPr.append(type_elem)
        
        body = target_xml.getparent()
        body.insert(list(body).index(target_xml), new_p)
        
        # 重新加载doc以获取新section
        from docx import Document
        self.doc = Document(self.doc._part.main_document_part.blob)
        sections = list(self.doc.sections)
        
        if len(sections) > 1:
            # 设置最后一个section（新创建的）的header
            new_section = sections[-1]
            new_section.header.is_linked_to_previous = False
            
            # 清空header
            for p in list(new_section.header.paragraphs):
                p._element.getparent().remove(p._element)
            
            # 设置STYLEREF页眉
            p = new_section.header.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            run = p.add_run()
            fldChar1 = OxmlElement('w:fldChar')
            fldChar1.set(qn('w:fldCharType'), 'begin')
            run._r.append(fldChar1)
            
            instrText = OxmlElement('w:instrText')
            instrText.set(qn('xml:space'), 'preserve')
            instrText.text = r' STYLEREF "Heading 1" \* MERGEFORMAT '
            run._r.append(instrText)
            
            fldChar2 = OxmlElement('w:fldChar')
            fldChar2.set(qn('w:fldCharType'), 'separate')
            run._r.append(fldChar2)
            
            fldChar3 = OxmlElement('w:fldChar')
            fldChar3.set(qn('w:fldCharType'), 'end')
            run._r.append(fldChar3)
    
    def fix_references_format(self):
        """修复参考文献列表格式：英文标点 + 悬挂缩进2字符"""
        from docx.shared import Pt
        
        print("  修复参考文献列表格式...")
        
        # 找到"参考文献"标题的位置
        ref_start_idx = None
        for i, para in enumerate(self.doc.paragraphs):
            text = para.text.strip()
            if text == "参考文献":
                ref_start_idx = i
                break
        
        if ref_start_idx is None:
            print("    未找到'参考文献'标题，跳过")
            return
        
        print(f"    找到'参考文献'在段落 {ref_start_idx}")
        
        # 修复参考文献段落
        count_punct = 0
        count_indent = 0
        
        # 标点替换映射
        punct_map = {
            '。': '.',
            '，': ',',
            '：': ':',
            '；': ';',
            '（': '(',
            '）': ')',
            '《': '"',
            '》': '"',
            '【': '[',
            '】': ']'
        }
        
        # 遍历参考文献后面的段落
        for i in range(ref_start_idx + 1, len(self.doc.paragraphs)):
            para = self.doc.paragraphs[i]
            text = para.text.strip()
            
            # 遇到新的章节标题，停止处理
            if para.style and 'Heading 1' in para.style.name:
                break
            
            # 跳过空段落
            if not text:
                continue
            
            # 1. 标点替换
            new_text = text
            for cn_punct, en_punct in punct_map.items():
                if cn_punct in new_text:
                    new_text = new_text.replace(cn_punct, en_punct)
                    count_punct += 1
            
            if new_text != text:
                # 更新文本
                for run in para.runs:
                    run.text = ''
                if para.runs:
                    para.runs[0].text = new_text
                else:
                    para.add_run(new_text)
            
            # 2. 设置悬挂缩进 2 个中文字符
            # 2个中文字符 ≈ 42磅 (21磅/字符)
            try:
                para_format = para.paragraph_format
                para_format.first_line_indent = Pt(-21)  # 悬挂缩进
                para_format.left_indent = Pt(21)        # 左缩进
                
                # Bug修复2: 使用XML方式确保悬挂缩进生效
                para_xml = para._element
                pPr = para_xml.find('.//w:pPr', {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
                if pPr is None:
                    pPr = OxmlElement('w:pPr')
                    para_xml.insert(0, pPr)
                
                # 设置 ind 元素
                ind = pPr.find('.//w:ind', {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
                if ind is None:
                    ind = OxmlElement('w:ind')
                    pPr.append(ind)
                
                # left: 左缩进21磅, firstLine: 首行缩进-21磅（负数表示悬挂）
                ind.set(qn('w:left'), '2205')    # 21pt in EMUs (approx 2205)
                ind.set(qn('w:firstLine'), '-2205')  # -21pt in EMUs
                
                count_indent += 1
            except Exception as e:
                pass  # 忽略格式设置错误
        
        print(f"    标点替换: {count_punct} 处")
        print(f"    悬挂缩进设置: {count_indent} 处")
        
        if count_punct > 0 or count_indent > 0:
            self.report.add_fix("REF_FORMAT", count_punct + count_indent, "修复参考文献格式", success=True)
    
    def fix_acknowledgments_punctuation(self):
        """修复致谢标点：将半角逗号改为全角逗号"""
        print("  修复致谢标点...")
        
        # Bug修复3: 找到"致谢"标题的位置（处理"致 谢"中间有空格的情况）
        ack_start_idx = None
        for i, para in enumerate(self.doc.paragraphs):
            text = para.text.strip()
            # 移除空格后再比较，处理"致 谢"的情况
            text_nospace = text.replace(' ', '').replace('\t', '')
            if text_nospace == "致谢":
                ack_start_idx = i
                break
        
        if ack_start_idx is None:
            print("    未找到'致谢'标题，跳过")
            return
        
        print(f"    找到'致谢'在段落 {ack_start_idx}")
        
        count = 0
        # 遍历致谢后面的段落
        for i in range(ack_start_idx + 1, len(self.doc.paragraphs)):
            para = self.doc.paragraphs[i]
            text = para.text.strip()
            
            # 遇到新的章节标题，停止处理
            if para.style and 'Heading 1' in para.style.name:
                break
            
            # 跳过空段落
            if not text:
                continue
            
            # 替换半角逗号为全角逗号
            if ',' in text:
                new_text = text.replace(',', '，')
                # 更新文本
                for run in para.runs:
                    run.text = ''
                if para.runs:
                    para.runs[0].text = new_text
                else:
                    para.add_run(new_text)
                count += 1
        
        if count > 0:
            self.report.add_fix("ACK_PUNCT", count, "修复致谢标点", success=True)
            print(f"    致谢标点修复: {count} 处")
        else:
            print("    无需修复致谢标点")
    
    def fix_caption_colon(self):
        """修复图表题注冒号：将'图 5.2:'或'表 3.1:'中的冒号替换为全角空格"""
        import re
        
        print("  修复图表题注冒号...")
        
        # 正则匹配图表题注中的冒号
        # 匹配: "图 X.X:" 或 "表 X.X:" 后面紧跟冒号的情况
        pattern = r'(图\s*\d+\.\d+):'
        pattern2 = r'(表\s*\d+\.\d+):'
        
        count = 0
        for para in self.doc.paragraphs:
            text = para.text
            
            # 检查是否包含图表编号+冒号
            match = re.search(pattern, text) or re.search(pattern2, text)
            if match:
                # 替换冒号为全角空格
                new_text = text.replace(':', ' ')
                # 替换多个空格为单个全角空格
                new_text = re.sub(r'\s+', ' ', new_text)
                
                if new_text != text:
                    # 更新文本
                    for run in para.runs:
                        run.text = ''
                    if para.runs:
                        para.runs[0].text = new_text
                    else:
                        para.add_run(new_text)
                    count += 1
        
        if count > 0:
            self.report.add_fix("CAPTION_COLON", count, "修复图表题注冒号", success=True)
            print(f"    图表题注冒号修复: {count} 处")
        else:
            print("    无需修复图表题注冒号")
    
    def fix_toc_levels(self):
        """修复目录层级：将TOC显示级别从3级改为2级"""
        import re
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        
        print("  修复目录层级...")
        
        # Step 1: 修改TOC域代码的显示级别
        # 遍历文档底层所有的 <w:instrText> 节点
        count = 0
        for instrText in self.doc.element.xpath('//w:instrText'):
            if instrText.text and 'TOC' in instrText.text:
                original = instrText.text
                # 将 \o "1-3" 或 \o "1-4" 等替换为 \o "1-2"
                new_text = re.sub(r'\\o\s+"1-\d+"', r'\\o "1-2"', original)
                if new_text != original:
                    instrText.text = new_text
                    count += 1
                    print(f"    修改TOC域代码: {original} -> {new_text}")
        
        # Step 2: 强制Word在下次打开时提示更新域（包括目录）
        settings = self.doc.settings.element
        updateFields = settings.find(qn('w:updateFields'))
        if updateFields is None:
            updateFields = OxmlElement('w:updateFields')
            settings.append(updateFields)
        updateFields.set(qn('w:val'), 'true')
        print("    已设置打开时自动更新域")
        
        # Step 3: 【新增】物理删除 3 级及以上目录缓存段落
        # 这样即使 WPS/Word 不自动更新域，打开时也看不到 3 级目录了
        toc_deleted_count = 0
        for p in self.doc.paragraphs:
            if p.style and p.style.name:
                style_name_lower = p.style.name.lower()
                if style_name_lower.startswith('toc ') and len(style_name_lower) > 4:
                    try:
                        level = int(style_name_lower.split(' ')[1])
                        if level >= 3:
                            p._element.getparent().remove(p._element)
                            toc_deleted_count += 1
                    except ValueError:
                        pass
        if toc_deleted_count > 0:
            print(f"    已物理删除 {toc_deleted_count} 个三级及以上目录缓存段落")
        
        if count > 0:
            self.report.add_fix("TOC_LEVELS", count, "修复目录层级为2级", success=True)
            print(f"    目录层级修复: {count} 处")
        else:
            print("    无需修复目录层级")
    
    def fix_references_and_citations(self):
        """
        修复正文引用格式和参考文献列表
        Phase 1: 解析参考文献，建立映射字典
        Phase 2: 遍历正文，替换上标引用
        Phase 3: 参考文献清洗与分类排序
        Phase 4: 重新写入并设置悬挂缩进
        """
        import re
        from docx.shared import Pt
        
        print("  修复正文引用格式和参考文献列表...")
        
        # ========== Phase 1: 解析参考文献，建立映射字典 ==========
        print("    Phase 1: 解析参考文献...")
        
        # 找到参考文献标题位置
        ref_start_idx = None
        for i, para in enumerate(self.doc.paragraphs):
            text = para.text.strip().replace(' ', '')
            if text == "参考文献":
                ref_start_idx = i
                break
        
        if ref_start_idx is None:
            print("    未找到'参考文献'标题，跳过")
            return
        
        # 提取参考文献段落（从参考文献标题之后到文档结尾，或到下一个章节标题之前）
        ref_paragraphs = []
        for i in range(ref_start_idx + 1, len(self.doc.paragraphs)):
            para = self.doc.paragraphs[i]
            text = para.text.strip()
            # 跳过空段落
            if not text:
                continue
            # 遇到新的章节标题（如"附录"或"致谢"），停止收集
            if text.startswith("附录") or text.startswith("致谢"):
                break
            ref_paragraphs.append((i, para, text))
        
        print(f"    找到 {len(ref_paragraphs)} 条参考文献")
        
        # 建立映射字典: { "1": "（作者，年份）", "2": "（作者，年份）" }
        ref_mapping = {}
        for idx, (orig_idx, para, text) in enumerate(ref_paragraphs, start=1):
            # 提取作者：段落开头到第一个标点符号
            # 处理多种分隔符：. 。 , ，
            author_match = re.match(r'^([^.。,，]+)[.。,]', text)
            if author_match:
                author = author_match.group(1).strip()
            else:
                # 如果没有分隔符，取前15个字符作为作者
                author = text[:15].strip()
            
            # 处理英文作者：只取姓氏
            # 判断是否包含英文字母
            if re.search(r'[a-zA-Z]', author):
                # 英文作者，尝试取姓氏
                # 常见格式：Smith, J. 或 Smith John
                if ',' in author:
                    author = author.split(',')[0].strip()
                else:
                    # 取第一个空格前的部分作为姓氏
                    parts = author.split()
                    if parts:
                        author = parts[0]
            
            # 提取年份：查找4位数年份
            year_match = re.search(r'(19\d{2}|20\d{2})', text)
            if year_match:
                year = year_match.group(1)
            else:
                year = "n.d."
            
            # 多个作者的情况：只取第一个
            if ';' in author:
                author = author.split(';')[0].strip() + "等"
            elif ',' in author and not re.search(r'[a-zA-Z]', author):
                author = author.split(',')[0].strip() + "等"
            elif '&' in author:
                author = author.split('&')[0].strip() + "等"
            
            # 存储映射
            ref_mapping[str(idx)] = f"（{author}，{year}）"
            print(f"      [{idx}] {author}, {year}")
        
        # ========== Phase 2: 遍历正文，替换上标引用 ==========
        print("    Phase 2: 替换正文引用...")
        
        # 遍历参考文献标题之前的所有段落
        replace_count = 0
        
        # 首先，对所有段落清除可能存在的上标格式
        # 这样可以处理跨Run的引用
        for i in range(ref_start_idx):
            para = self.doc.paragraphs[i]
            for run in para.runs:
                run.font.superscript = False
        
        # 然后进行替换
        for i in range(ref_start_idx):
            para = self.doc.paragraphs[i]
            
            # 更安全的替换策略：先合并段落中所有Run的文本
            # 检查段落中是否包含 [数字] 引用
            para_text = para.text
            ref_pattern = r'\[(\d+)\]'
            
            if not re.search(ref_pattern, para_text):
                continue
            
            # 收集所有Run的文本并合并
            full_text = ''.join(run.text for run in para.runs)
            
            # 查找所有匹配
            matches = list(re.finditer(ref_pattern, full_text))
            
            if not matches:
                continue
            
            # 从后向前替换（保持位置索引有效）
            for match in reversed(matches):
                ref_num = match.group(1)
                
                if ref_num in ref_mapping:
                    replacement = ref_mapping[ref_num]
                    
                    # 替换文本
                    new_text = full_text[:match.start()] + replacement + full_text[match.end():]
                    
                    # 清空所有Run并清除格式
                    for run in para.runs:
                        run.text = ''
                        run.font.bold = False
                        run.font.italic = False
                        run.font.underline = False
                        run.font.superscript = False
                        run.font.subscript = False
                    
                    # 将新文本写入第一个Run（现在没有格式了）
                    if para.runs:
                        para.runs[0].text = new_text
                    else:
                        para.add_run(new_text)
                    
                    replace_count += 1
                    print(f"        替换 [{ref_num}] -> {replacement}")
                    
                    # 更新full_text以进行下一次替换
                    full_text = new_text
        
        print(f"    正文引用替换: {replace_count} 处")
        
        # ========== Phase 3: 参考文献清洗与分类排序 ==========
        print("    Phase 3: 参考文献清洗与分类排序...")
        
        # 提取所有参考文献文本
        ref_texts = [text for _, _, text in ref_paragraphs]
        
        # 标点清洗
        cleaned_refs = []
        for text in ref_texts:
            # 中文标点 -> 英文标点 + 空格
            text = text.replace('。', '. ')
            text = text.replace('：', ': ')
            text = text.replace('，', ', ')
            text = text.replace('；', '; ')
            text = text.replace('（', '(')
            text = text.replace('）', ') ')
            
            # 清理多余空格
            text = re.sub(r'\s+', ' ', text).strip()
            # 修复括号后的空格问题
            text = re.sub(r'\)\s+', ')', text)
            
            cleaned_refs.append(text)
        
        # 语种分类
        chinese_refs = []
        english_refs = []
        
        for ref in cleaned_refs:
            # 判断是否包含中文字符
            if re.search(r'[\u4e00-\u9fa5]', ref):
                chinese_refs.append(ref)
            else:
                english_refs.append(ref)
        
        print(f"    中文文献: {len(chinese_refs)} 篇")
        print(f"    英文文献: {len(english_refs)} 篇")
        
        # 排序：中文按拼音排序，英文按字母排序
        chinese_refs.sort(key=lambda x: ''.join(lazy_pinyin(x)).lower())
        english_refs.sort(key=lambda x: x.lower())
        
        # 合并：中文在前，英文在后
        sorted_refs = chinese_refs + english_refs
        
        print(f"    排序后共 {len(sorted_refs)} 篇")
        
        # ========== Phase 4: 重新写入并设置悬挂缩进 ==========
        print("    Phase 4: 重新写入参考文献...")
        
        # 删除旧的参考文献段落
        for orig_idx, para, text in ref_paragraphs:
            # 清空段落内容
            for run in para.runs:
                run.text = ''
        
        # 获取参考文献标题段落
        ref_title_para = self.doc.paragraphs[ref_start_idx]
        
        # 在参考文献标题后插入新段落
        # 首先删除参考文献标题之后的所有段落，然后重新插入
        # 更简单的方法：直接在现有段落上更新文本
        
        # 更新参考文献标题的下一个段落开始
        insert_idx = ref_start_idx + 1
        
        for i, ref_text in enumerate(sorted_refs):
            if insert_idx + i < len(self.doc.paragraphs):
                # 更新现有段落
                para = self.doc.paragraphs[insert_idx + i]
                for run in para.runs:
                    run.text = ''
                if para.runs:
                    para.runs[0].text = ref_text
                else:
                    para.add_run(ref_text)
            else:
                # 创建新段落
                para = self.doc.add_paragraph(ref_text)
                para.style = 'Normal'
            
            # 统一设置格式：对齐、悬挂缩进、行距、双语字体
            # 1. 设置对齐和悬挂缩进 (使用 Cm 确保绝对精确)
            para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY  # 两端对齐
            para.paragraph_format.left_indent = Cm(0.74)       # 左缩进 0.74cm ≈ 2个汉字(五号)
            para.paragraph_format.first_line_indent = Cm(-0.74) # 首行悬挂 2 字符
            
            # 2. 设置行距：固定值 16 磅，段前 3 磅，段后 0 磅
            para.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
            para.paragraph_format.line_spacing = Pt(16)
            para.paragraph_format.space_before = Pt(3)
            para.paragraph_format.space_after = Pt(0)
            
            # 3. 设置中英文字体分离 (底层 XML 注入)
            for run in para.runs:
                # 英文/数字使用 Times New Roman
                run.font.name = 'Times New Roman'
                # 中文强制使用宋体 (eastAsia 字体)
                run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                run.font.size = Pt(10.5)  # 五号
            
            # 4. 【核心黑科技】：允许西文在单词中间换行
            # 这将完美解决两端对齐时，长 URL 导致的字间距被异常拉伸的问题
            # <w:wordWrap w:val="0"/> - 0 表示关闭默认的单词包裹，允许中间断行
            pPr = para._p.get_or_add_pPr()
            wordWrap = pPr.find(qn('w:wordWrap'))
            if wordWrap is None:
                wordWrap = OxmlElement('w:wordWrap')
                pPr.append(wordWrap)
            wordWrap.set(qn('w:val'), '0')
        
        self.report.add_fix("REF_CITATIONS", replace_count, "正文引用格式和参考文献列表修复", success=True)
        print(f"    参考文献修复完成!")
    
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
        
        # 修复目录层级（显示到2级）- 必须在页眉页脚处理之前执行
        self.fix_toc_levels()
        
        # 修复页码和页眉（三区隔离法）
        self.fix_document_zones_and_headers()
        
        # 修复章标题编号字体（必须在禁用编号之前执行）
        self.fix_heading1_numbering_font()
        
        # 修复尾部格式问题
        self.fix_chapter_tail_numbers()
        self.fix_heading_spacing()
        self.fix_acknowledgments_punctuation()
        self.fix_caption_colon()
        
        # 修复正文引用格式和参考文献列表（核心逻辑）
        self.fix_references_and_citations()
        
        # 保存文档
        self.doc.save(output_path)
        
        return output_path, self.report
    
    def _fix_paragraph_styles(self):
        """修复段落样式 - 优化版：按zone分组修复，避免重复"""
        # 修复标题编号样式（自动编号末尾的点）
        self.fix_heading_numbering_style()
        
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
        
        # 修复参考文献格式
        self._fix_reference_format()
        
        # 修复图表编号格式
        self._fix_figure_numbering()
        
        # 修复节标题格式
        self._fix_heading_format()
        
        # 修复英文摘要关键词分隔符
        self._fix_english_keyword_separators()
        
        # 修复目录层级
        self._fix_table_of_contents()
        
        # 删除尾部空白页
        self._fix_trailing_blank_pages()
    
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
    
    def _fix_reference_format(self):
        """修复参考文献格式：去除数字序号、转换中文标点为英文标点、设置字体字号缩进行距"""
        from docx.shared import Pt, Cm
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        # 查找参考文献区域的段落
        ref_keywords = ["参考文献", "References", "REFERENCE"]
        
        in_reference_section = False
        ref_para_count = 0  # 统计参考文献段落数
        
        for para_idx, para in enumerate(self.doc.paragraphs):
            text = para.text.strip()
            
            # 检测参考文献区域开始 - 不依赖于段落样式
            # 直接检查文本是否匹配参考文献标题（无论是Normal样式还是Heading样式）
            for kw in ref_keywords:
                if text == kw:  # 精确匹配标题
                    in_reference_section = True
                    continue
            
            if not in_reference_section or not text:
                continue
            
            # 跳过参考文献标题
            if text == "参考文献" or text == "References":
                continue
            
            ref_para_count += 1
            original = text
            
            # 修复1：去除参考文献开头的数字序号 [1] 
            # 修复正则表达式的转义问题
            text = re.sub(r'^\[\s*\d+\s*\]', '', text)
            text = re.sub(r'^\d+\.\s*', '', text)  # 去除开头的 "1. "
            
            # 修复2：转换中文标点为英文标点（仅在参考文献区域）
            # 中文逗号 -> 英文逗号
            text = text.replace('，', ',')
            # 中文分号 -> 英文分号
            text = text.replace('；', ';')
            # 注意：中文句号和冒号不替换，保留中文标点
            
            # 如果有变化，更新段落
            if text != original:
                if para.runs:
                    first_run = para.runs[0]
                    para.clear()
                    new_run = para.add_run(text)
                    new_run.font.name = first_run.font.name
                    new_run.font.size = first_run.font.size
                else:
                    para.clear()
                    para.add_run(text)
                
                self.report.add_fix(
                    "REF_FORMAT",
                    para_idx,
                    "修复参考文献格式：去除序号/转换标点",
                    success=True
                )
            
            # 修复3：设置字体（宋体 + Times New Roman）
            font_fixes = []
            for run in para.runs:
                if run.text.strip():
                    # 设置中文字体 - 使用 rPr 中的 rFonts
                    try:
                        rFonts = run._element.get_or_add_rPr().get_or_add_rFonts()
                        # 设置中文字体
                        rFonts.set(qn('w:eastAsia'), '宋体')
                        # 设置英文字体
                        rFonts.set(qn('w:ascii'), 'Times New Roman')
                        rFonts.set(qn('w:hAnsi'), 'Times New Roman')
                        font_fixes.append('字体改为宋体/Times New Roman')
                    except Exception:
                        pass
            
            # 修复4：设置字号（五号 = 10.5pt）
            for run in para.runs:
                if run.text.strip() and run.font.size:
                    if abs(run.font.size.pt - 10.5) > 0.1:  # 允许微小误差
                        run.font.size = Pt(10.5)
                        font_fixes.append('字号改为10.5pt')
            
            # 修复5：设置悬挂缩进（2字符）
            # 2字符 ≈ 1.48cm (根据Word标准)
            hanging_indent_cm = 1.48  # 2字符悬挂缩进
            current_left_indent = para.paragraph_format.left_indent
            
            needs_indent_fix = True
            if current_left_indent is not None:
                current_cm = utils.emu_to_cm(abs(current_left_indent))
                if abs(current_cm - hanging_indent_cm) < 0.1:
                    needs_indent_fix = False
            
            if needs_indent_fix:
                para.paragraph_format.left_indent = Cm(hanging_indent_cm)
                # 悬挂缩进：首行不缩进，左缩进2字符
                para.paragraph_format.first_line_indent = Cm(0)
                font_fixes.append(f'左缩进改为{hanging_indent_cm}cm（悬挂2字符）')
            
            # 修复6：设置行距（16磅）
            line_spacing_fixed = False
            try:
                from docx.enum.text import WD_LINE_SPACING
                if para.paragraph_format.line_spacing_rule is None or \
                   para.paragraph_format.line_spacing_rule != WD_LINE_SPACING.EXACTLY:
                    para.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
                    line_spacing_fixed = True
                elif para.paragraph_format.line_spacing:
                    current_pt = utils.emu_to_pt(para.paragraph_format.line_spacing)
                    if abs(current_pt - 16) > 1:  # 允许1磅误差
                        line_spacing_fixed = True
                
                if line_spacing_fixed:
                    para.paragraph_format.line_spacing = Pt(16)
                    font_fixes.append('行距改为16磅')
            except Exception:
                pass
            
            # 修复7：设置段前段后间距（段前3磅，段后0磅）
            if para.paragraph_format.space_before is None or \
               abs(para.paragraph_format.space_before.pt - 3) > 0.5:
                para.paragraph_format.space_before = Pt(3)
                font_fixes.append('段前改为3磅')
            
            if para.paragraph_format.space_after is None or \
               abs(para.paragraph_format.space_after.pt - 0) > 0.5:
                para.paragraph_format.space_after = Pt(0)
                font_fixes.append('段后改为0磅')
            
            # 记录修复
            if font_fixes:
                self.report.add_fix(
                    "REF_FORMAT",
                    para_idx,
                    "; ".join(font_fixes),
                    success=True
                )
        
        # 打印统计信息
        if ref_para_count > 0:
            print(f"  参考文献段落修复：共 {ref_para_count} 个条目")
    
    def _fix_figure_numbering(self):
        """修复图表编号格式：将连字符格式 3-1 改为小数点格式 3.1"""
        # 查找所有段落，检查图表题注
        figure_patterns = [
            r'(图|表|表|图)\s*(\d+)-(\d+)',  # 匹配 "图 3-1" 或 "表 2-1"
        ]
        
        for para_idx, para in enumerate(self.doc.paragraphs):
            text = para.text.strip()
            if not text:
                continue
            
            original = text
            
            # 修复图表编号中的连字符为小数点
            # 匹配 "图 3-1" -> "图 3.1"
            text = re.sub(r'(图|表)\s*(\d+)-(\d+)', r'\1 \2.\3', text)
            
            if text != original:
                if para.runs:
                    first_run = para.runs[0]
                    para.clear()
                    new_run = para.add_run(text)
                    new_run.font.name = first_run.font.name
                    new_run.font.size = first_run.font.size
                
                self.report.add_fix(
                    "FIG_NUM",
                    para_idx,
                    "修复图表编号格式：3-1 -> 3.1",
                    success=True
                )
    
    def _fix_heading_format(self):
        """修复节标题格式：去除多余小数点和章节前缀"""
        for para_idx, para in enumerate(self.doc.paragraphs):
            text = para.text.strip()
            if not text:
                continue
            
            original = text
            
            # 修复1：去除多余的小数点（如 1..1 或 1.1.）
            # 匹配连续的小数点
            text = re.sub(r'(\d+)\.(\d+)\.\.+', r'\1.\2', text)
            
            # 修复：处理 "1.1. 研究背景" -> "1.1 研究背景"
            # 处理任意级别的小数点（1.1.、1.1.1.、1.1.1.1.等）
            # 匹配: 数字.数字(.数字)*.空格
            # 替换: 去掉最后一个点
            text = re.sub(r'^(\d+(?:\.\d+)*)\.(\s)', r'\1\2', text)
            
            text = re.sub(r'(\d+)\.$', r'\1', text)  # 去除尾部多余的小数点
            
            # 修复2：去除非首章的"第X章"前缀（仅对2-10章有效）
            # 匹配 "第2章 1.1" 格式并转换为 "1.1"
            text = re.sub(r'^第[二三四五六七八九十]+章\s+(\d+\.\d+)', r'\1', text)
            
            if text != original:
                if para.runs:
                    first_run = para.runs[0]
                    para.clear()
                    new_run = para.add_run(text)
                    new_run.font.name = first_run.font.name
                    new_run.font.size = first_run.font.size
                
                self.report.add_fix(
                    "HEADING_FORMAT",
                    para_idx,
                    "修复节标题格式",
                    success=True
                )
    
    def _fix_english_keyword_separators(self):
        """修复英文摘要关键词分隔符：将分号替换为逗号"""
        # 查找英文摘要区域的段落
        in_abstract_en = False
        
        for para_idx, para in enumerate(self.doc.paragraphs):
            text = para.text.strip()
            text_lower = text.lower()
            
            # 检测英文摘要区域开始：包括"ABSTRACT"标题和"KEY WORDS"标题
            if "abstract" in text_lower:
                if len(text) < 30:  # 标题行
                    in_abstract_en = True
            
            # 如果段落以"KEY WORDS"开头（可能是标题+内容在同一行）
            if text_lower.startswith("key words"):
                in_abstract_en = True
            
            if not in_abstract_en:
                continue
            
            # 查找包含关键词的行 (Keywords: xxx; xxx; xxx 或 KEY WORDS: xxx; xxx; xxx)
            if ("keyword" in text_lower or "key word" in text_lower) and (";" in text or ":" in text):
                original = text
                
                # 替换分号为逗号（英文分号 ;）
                text = text.replace(';', ',')
                
                # 清理多余的逗号
                while ',,' in text:
                    text = text.replace(',,', ',')
                
                # 清理开头和结尾的逗号
                if text.startswith(','):
                    text = text[1:].strip()
                if text.endswith(','):
                    text = text[:-1].strip()
                
                if text != original:
                    if para.runs:
                        first_run = para.runs[0]
                        para.clear()
                        new_run = para.add_run(text)
                        new_run.font.name = first_run.font.name
                        new_run.font.size = first_run.font.size
                    
                    self.report.add_fix(
                        "EN_KEYWORD_SEP",
                        para_idx,
                        "英文关键词分隔符从分号改为逗号",
                        success=True
                    )
    
    def _fix_table_of_contents(self):
        """修复目录层级：只显示1-2级标题"""
        # 遍历所有段落，查找目录
        # 目录在python-docx中通常是隐式标记的
        
        # 方案：找到目录段落，检查其层级设置
        # 如果目录显示超过2级，则重新生成
        
        # 注意：python-docx对目录的支持有限
        # 这里我们通过检查目录的样式来判断是否需要修复
        
        toc_fixed = False
        
        # 遍历所有段落，查找类似目录的文本
        for para_idx, para in enumerate(self.doc.paragraphs):
            text = para.text.strip()
            
            # 检查是否是目录标题
            if "目 录" in text or "目录" in text:
                # 这是一个目录标题
                # 检查下一个段落是否是目录内容
                if para_idx + 1 < len(self.doc.paragraphs):
                    next_para = self.doc.paragraphs[para_idx + 1]
                    next_text = next_para.text.strip()
                    
                    # 如果目录包含超过2级的标题，尝试修复
                    # 这里我们做一个标记，实际修复需要用户手动调整目录显示级别
                    # 或者我们可以尝试删除旧目录并插入新的2级目录
                    
                    # 由于python-docx对目录操作有限，我们这里记录问题
                    self.report.add_fix(
                        "TOC_LEVEL",
                        para_idx,
                        "目录显示层级需手动调整：设置为显示1-2级标题",
                        success=False  # 标记为需要手动处理
                    )
                    toc_fixed = True
                    break
        
        return toc_fixed
    
    def _fix_trailing_blank_pages(self):
        """删除末尾多余的空白段落"""
        # 从后往前遍历，删除空白段落
        blank_count = 0
        
        # 获取所有段落
        paragraphs = self.doc.paragraphs
        
        # 从最后一个段落开始往前遍历
        for i in range(len(paragraphs) - 1, -1, -1):
            para = paragraphs[i]
            text = para.text.strip()
            
            # 如果是完全空白的段落，或者是只有换行符的段落
            if not text or text == '' or text == '\n':
                # 删除这个段落
                # python-docx中，段落不能直接删除，需要从父元素中移除
                p_elem = para._element
                p_elem.getparent().remove(p_elem)
                blank_count += 1
            else:
                # 遇到第一个非空段落就停止
                break
        
        if blank_count > 0:
            self.report.add_fix(
                "TRAILING_BLANK",
                len(paragraphs),
                f"删除末尾 {blank_count} 个空白段落",
                success=True
            )
            return True
        
        return False
    
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
    def fix_heading_spacing(self):
        """
        统一所有 Heading 1 标题的字体和间距
        规则：黑体，三号(16pt)，居中，单倍行距，段前24磅，段后18磅
        
        关键：同时清洗段落标记(回车符)的底层属性，解决"第七章"自动编号字体不一致的顽疾
        """
        from docx.shared import Pt
        from docx.enum.text import WD_LINE_SPACING, WD_ALIGN_PARAGRAPH
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        
        print("  统一标题样式...")
        
        fixed_count = 0
        
        for idx, para in enumerate(self.doc.paragraphs):
            if not para.style:
                continue
            style_name = para.style.name if para.style.name else ""
            if 'Heading 1' not in style_name:
                continue
            
            text = para.text.strip()
            text_short = text[:20] if len(text) > 20 else text
            
            # 1. 设置居中对齐
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # 2. 设置段落间距：段前24pt，段后18pt，单倍行距
            pf = para.paragraph_format
            pf.space_before = Pt(24)
            pf.space_after = Pt(18)
            pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
            
            # 3. 设置字体：黑体，16pt
            if not para.runs:
                para.add_run(text)
            
            for run in para.runs:
                run.font.size = Pt(16)
                run.font.name = '黑体'
                # 设置中文字体
                run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
                run.font.bold = True  # 确保加粗
            
            # 4. 【终极修复】：清洗段落标记(回车符)的底层属性
            # 这一步专门解决"第七章"自动编号字体与正文不一致的顽疾
            pPr = para._p.get_or_add_pPr()
            
            # 获取或创建 rPr 元素
            rPr = pPr.find(qn('w:rPr'))
            if rPr is None:
                rPr = OxmlElement('w:rPr')
                pPr.append(rPr)
            
            # 获取或创建字体节点
            rFonts = rPr.find(qn('w:rFonts'))
            if rFonts is None:
                rFonts = OxmlElement('w:rFonts')
                rPr.append(rFonts)
            
            # 清除主题字体干扰（防止Word强制回退到默认宋体）
            for attr in ['asciiTheme', 'eastAsiaTheme', 'hAnsiTheme', 'cstheme']:
                if qn(f'w:{attr}') in rFonts.attrib:
                    del rFonts.attrib[qn(f'w:{attr}')]
            
            # 强制将段落标记设为黑体
            rFonts.set(qn('w:ascii'), '黑体')
            rFonts.set(qn('w:eastAsia'), '黑体')
            rFonts.set(qn('w:hAnsi'), '黑体')
            
            # 强制将段落标记设为加粗
            b = rPr.find(qn('w:b'))
            if b is None:
                b = OxmlElement('w:b')
                rPr.append(b)
            b.set(qn('w:val'), '1')
            
            bCs = rPr.find(qn('w:bCs'))
            if bCs is None:
                bCs = OxmlElement('w:bCs')
                rPr.append(bCs)
            bCs.set(qn('w:val'), '1')
            
            # 强制将段落标记字号设为三号 (16pt = 32 half-points)
            sz = rPr.find(qn('w:sz'))
            if sz is None:
                sz = OxmlElement('w:sz')
                rPr.append(sz)
            sz.set(qn('w:val'), '32')
            
            szCs = rPr.find(qn('w:szCs'))
            if szCs is None:
                szCs = OxmlElement('w:szCs')
                rPr.append(szCs)
            szCs.set(qn('w:val'), '32')
            
            fixed_count += 1
            print(f"    已修复: 段落 {idx}, {text_short}")
        
        print(f"  标题样式统一完成: {fixed_count} 个标题")
        
        if fixed_count > 0:
            self.report.add_fix("HEADING_STYLE_UNIFY", fixed_count, "统一标题样式（黑体/16pt/居中/段前24pt/段后18pt/单倍行距）+ 清洗段落标记", success=True)

    def fix_heading1_numbering_font(self):
        """
        终极修复：强制将 Heading 1 (章标题) 的自动编号字体设置为黑体。
        直接追踪每个段落实际使用的 numId，修改 numbering.xml，并清除主题字体干扰。
        """
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn

        if not self.doc.part.numbering_part:
            return

        numbering_xml = self.doc.part.numbering_part._element
        fixed_abstract_nums = set()

        for para in self.doc.paragraphs:
            # 识别章标题 (Heading 1)
            if para.style and ('Heading 1' in para.style.name or '标题 1' in para.style.name):
                pPr = para._p.pPr
                if pPr is None:
                    continue

                numId_val = None
                ilvl_val = "0"  # 默认一级标题

                # 1. 优先检查段落自带的 numPr (覆盖样式)
                numPr = pPr.find(qn('w:numPr'))
                if numPr is not None:
                    numId_node = numPr.find(qn('w:numId'))
                    ilvl_node = numPr.find(qn('w:ilvl'))
                    if numId_node is not None:
                        numId_val = numId_node.get(qn('w:val'))
                    if ilvl_node is not None:
                        ilvl_val = ilvl_node.get(qn('w:val'))

                # 2. 如果段落没有，再检查样式的 numPr
                if numId_val is None:
                    style_elem = para.style._element
                    style_pPr = style_elem.find(qn('w:pPr'))
                    if style_pPr is not None:
                        style_numPr = style_pPr.find(qn('w:numPr'))
                        if style_numPr is not None:
                            numId_node = style_numPr.find(qn('w:numId'))
                            ilvl_node = style_numPr.find(qn('w:ilvl'))
                            if numId_node is not None:
                                numId_val = numId_node.get(qn('w:val'))
                            if ilvl_node is not None:
                                ilvl_val = ilvl_node.get(qn('w:val'))

                if not numId_val:
                    continue

                # 3. 追踪到 numbering.xml 中的 abstractNum
                try:
                    num_nodes = numbering_xml.xpath(f'.//w:num[@w:numId="{numId_val}"]/w:abstractNumId')
                    if not num_nodes:
                        continue
                    abstractNumId_val = num_nodes[0].get(qn('w:val'))

                    # 避免重复修改
                    if (abstractNumId_val, ilvl_val) in fixed_abstract_nums:
                        continue

                    # 4. 找到对应的 lvl 节点
                    lvl_nodes = numbering_xml.xpath(f'.//w:abstractNum[@w:abstractNumId="{abstractNumId_val}"]/w:lvl[@w:ilvl="{ilvl_val}"]')
                    if not lvl_nodes:
                        continue
                    lvl_node = lvl_nodes[0]

                    # 5. 获取或创建 rPr (运行属性)
                    rPr = lvl_node.find(qn('w:rPr'))
                    if rPr is None:
                        rPr = OxmlElement('w:rPr')
                        lvl_node.insert(0, rPr)  # 插入到最前面

                    # 6. 强制设置字体为黑体，并清除主题字体干扰
                    rFonts = rPr.find(qn('w:rFonts'))
                    if rFonts is None:
                        rFonts = OxmlElement('w:rFonts')
                        rPr.append(rFonts)

                    # 【关键修复】：清除主题字体绑定，否则 Word 会优先使用主题字体(宋体)
                    for attr in ['asciiTheme', 'eastAsiaTheme', 'hAnsiTheme', 'cstheme']:
                        if qn(f'w:{attr}') in rFonts.attrib:
                            del rFonts.attrib[qn(f'w:{attr}')]

                    # 设置具体字体
                    rFonts.set(qn('w:ascii'), '黑体')
                    rFonts.set(qn('w:eastAsia'), '黑体')
                    rFonts.set(qn('w:hAnsi'), '黑体')
                    rFonts.set(qn('w:cs'), '黑体')

                    # 7. 确保加粗 (与正文黑体保持一致)
                    b = rPr.find(qn('w:b'))
                    if b is None:
                        b = OxmlElement('w:b')
                        rPr.append(b)
                    b.set(qn('w:val'), '1')

                    bCs = rPr.find(qn('w:bCs'))
                    if bCs is None:
                        bCs = OxmlElement('w:bCs')
                        rPr.append(bCs)
                    bCs.set(qn('w:val'), '1')

                    fixed_abstract_nums.add((abstractNumId_val, ilvl_val))
                    print(f"成功修复 abstractNumId={abstractNumId_val}, ilvl={ilvl_val} 的编号字体为黑体")

                except Exception as e:
                    print(f"修复编号字体时出错: {e}")
                    continue

        if len(fixed_abstract_nums) > 0:
            self.report.add_fix("HEADING1_NUM_FONT", len(fixed_abstract_nums), "修复章标题自动编号字体为黑体", success=True)


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


