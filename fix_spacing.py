# -*- coding: utf-8 -*-
import re

with open('emba_checker/docx_autofixer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 fix_all 函数中调用 fix_chapter_tail_numbers 的位置
# 在其后添加调用新的 fix_heading_spacing 函数

old_code = '''        # 清理尾部章序号
        self.fix_chapter_tail_numbers()'''

new_code = '''        # 清理尾部章序号
        self.fix_chapter_tail_numbers()
        
        # 修复附录和致谢的段前间距和行距（Bug修复）
        self.fix_heading_spacing()'''

content = content.replace(old_code, new_code)

# 在文件末尾添加新函数
new_function = '''

    def fix_heading_spacing(self):
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
            self.report.add_fix("HEADING_SPACING", fixed, "附录和致谢标题间距修复", success=True)
'''

content = content + new_function

with open('emba_checker/docx_autofixer.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
