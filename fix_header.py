# -*- coding: utf-8 -*-
import re

with open('emba_checker/docx_autofixer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 _insert_section_break_before_paragraph 函数
old_code = '''    def _insert_section_break_before_paragraph(self, para_index):
        """在指定段落之前插入分节符（下一页）"""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        
        # 获取目标段落元素
        target_para = self.doc.paragraphs[para_index]
        target_xml = target_para._element
        
        # 在目标段落之前插入一个新的空段落，包含分节符
        # 创建一个新的p元素，包含分节符
        new_p = OxmlElement('w:p')
        
        # 创建pPr元素
        pPr = OxmlElement('w:pPr')
        new_p.append(pPr)
        
        # 创建sectPr（分节符）
        sectPr = OxmlElement('w:sectPr')
        pPr.append(sectPr)
        
        # 设置为下一页分节符
        type_elem = OxmlElement('w:type')
        type_elem.set(qn('w:val'), 'nextPage')
        sectPr.append(type_elem)
        
        # 获取父元素（通常是body）
        body = target_xml.getparent()
        
        # 在目标段落之前插入
        body.insert(list(body).index(target_xml), new_p)'''

new_code = '''    def _insert_section_break_before_paragraph(self, para_index):
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
            instrText.text = ' STYLEREF "Heading 1" \\* MERGEFORMAT '
            run._r.append(instrText)
            
            fldChar2 = OxmlElement('w:fldChar')
            fldChar2.set(qn('w:fldCharType'), 'separate')
            run._r.append(fldChar2)
            
            fldChar3 = OxmlElement('w:fldChar')
            fldChar3.set(qn('w:fldCharType'), 'end')
            run._r.append(fldChar3)'''

content = content.replace(old_code, new_code)

with open('emba_checker/docx_autofixer.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
