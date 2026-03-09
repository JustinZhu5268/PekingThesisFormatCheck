# -*- coding: utf-8 -*-
"""
Replace the fix_heading_spacing function with a comprehensive version
that unifies font size and spacing for ALL Heading 1 paragraphs
"""
import re

with open('emba_checker/docx_autofixer.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_func = '''    def fix_heading_spacing(self):
        """修复附录和致谢的段前间距和行距，防止被页眉遮挡"""
        from docx.shared import Pt
        from docx.enum.text import WD_LINE_SPACING
        
        print("  [DEBUG] Calling fix_heading_spacing...")
        
        fixed = 0
        for idx, para in enumerate(self.doc.paragraphs):
            if not para.style:
                continue
            style_name = para.style.name if para.style.name else ""
            if 'Heading 1' not in style_name:
                continue
            
            text = para.text.strip()
            
            # 检查是否是参考文献、附录或致谢
            is_target = False
            text_clean = text.replace(' ', '').replace('\t', '')
            if '参考文献' in text_clean or text_clean.startswith('附录') or '致谢' in text_clean:
                is_target = True
            
            if not is_target:
                continue
            
            pf = para.paragraph_format
            has_issue = False
            
            # 检查是否有异常的段前间距或固定行距
            if pf.space_before and pf.space_before.pt and pf.space_before.pt > 0:
                has_issue = True
            if pf.line_spacing_rule and pf.line_spacing_rule == WD_LINE_SPACING.EXACTLY:
                has_issue = True
            
            if has_issue:
                print(f"    [DEBUG] Fixing: para {idx}, text={text[:20]}")
                print(f"        before: space_before={pf.space_before.pt if pf.space_before else None}, line_spacing_rule={pf.line_spacing_rule}")
                
                # 清除段前间距
                pf.space_before = Pt(0)
                
                # 清除段后间距
                if pf.space_after:
                    pf.space_after = Pt(0)
                
                # 清除固定行距
                pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
                pf.line_spacing = 1.0
                
                print(f"        after: space_before={pf.space_before.pt if pf.space_before else None}, line_spacing_rule={pf.line_spacing_rule}")
                
                fixed += 1
        
        print(f"  [DEBUG] fix_heading_spacing completed, fixed={fixed}")
        if fixed > 0:
            self.report.add_fix("HEADING_SPACING", fixed, "附录和致谢标题间距修复", success=True)
        return False'''

new_func = '''    def fix_heading_spacing(self):
        """
        统一所有 Heading 1 标题的字体和间距
        - 字体大小：16pt（与第一章至第六章一致）
        - 段前间距：24pt（与第一章至第六章一致）
        - 行距：1.5倍
        - 加粗：否
        """
        from docx.shared import Pt
        from docx.enum.text import WD_LINE_SPACING
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
            
            # 1. 设置字体大小为 16pt
            if not para.runs:
                # 如果没有 run，添加一个
                para.add_run(text)
            
            for run in para.runs:
                run.font.size = Pt(16)
                run.font.bold = False
            
            # 2. 设置段落间距（通过 XML 级别）
            # 确保 pPr 存在
            pPr = para._element.find('.//w:pPr')
            if pPr is None:
                pPr = OxmlElement('w:pPr')
                para._element.insert(0, pPr)
            
            # 设置或更新 w:spacing
            spacing = pPr.find('.//w:spacing')
            if spacing is None:
                spacing = OxmlElement('w:spacing')
                pPr.append(spacing)
            
            # 设置段前 24pt (24 * 20 = 480 EMU)
            spacing.set(qn('w:before'), '480')
            # 设置段后 0
            spacing.set(qn('w:after'), '0')
            # 设置行距为 auto
            spacing.set(qn('w:lineRule'), 'auto')
            # 设置行距基准 1.5 倍 (240 = 1.5 * 160)
            spacing.set(qn('w:line'), '240')
            
            # 3. 同时通过 python-docx 设置（确保兼容）
            pf = para.paragraph_format
            pf.space_before = Pt(24)
            pf.space_after = Pt(0)
            pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
            pf.line_spacing = 1.5
            
            fixed_count += 1
            print(f"    已修复: 段落 {idx}, {text_short}")
        
        print(f"  标题样式统一完成: {fixed_count} 个标题")
        
        if fixed_count > 0:
            self.report.add_fix("HEADING_STYLE_UNIFY", fixed_count, "统一标题样式（字号16pt+段前24pt）", success=True)'''

# 替换
content = content.replace(old_func, new_func)

with open('emba_checker/docx_autofixer.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
