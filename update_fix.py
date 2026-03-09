# -*- coding: utf-8 -*-
with open('emba_checker/docx_autofixer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the fix_heading_spacing function
old_func = '''    def fix_heading_spacing(self):
        """修复附录和致谢的段前间距和行距，防止被页眉遮挡"""
        from docx.shared import Pt
        from docx.enum.text import WD_LINE_SPACING
        
        print("  修复附录和致谢标题间距...")
        
        fixed = 0
        for para in self.doc.paragraphs:
            if not para.style or 'Heading 1' not in para.style.name:
                continue
            
            text = para.text.strip()
            text_nospace = text.replace(' ', '').replace('\t', '')
            
            # 只处理附录和致谢
            if text_nospace.startswith("附录") or text_nospace.startswith("致谢"):
                pf = para.paragraph_format
                
                # 清除段前间距
                if pf.space_before:
                    pf.space_before = Pt(0)
                
                # 清除段后间距
                if pf.space_after:
                    pf.space_after = Pt(0)
                
                # 清除固定行距
                if pf.line_spacing_rule == WD_LINE_SPACING.EXACTLY:
                    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
                    pf.line_spacing = 1.0
                
                fixed += 1
                print(f"    已修复: {text[:20]}...")
        
        if fixed > 0:
            print(f"  标题间距修复完成: {fixed} 处")
            self.report.add_fix("HEADING_SPACING", fixed, "附录和致谢标题间距修复", success=True)'''

new_func = '''    def fix_heading_spacing(self):
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
            self.report.add_fix("HEADING_SPACING", fixed, "附录和致谢标题间距修复", success=True)'''

content = content.replace(old_func, new_func)

with open('emba_checker/docx_autofixer.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
