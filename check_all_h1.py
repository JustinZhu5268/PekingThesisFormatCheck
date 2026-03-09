# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
from docx.shared import Pt

doc = Document('data/test_已修复_20260309_095405.docx')

# 找所有Heading 1
print('All Heading 1 paragraphs:')
for i, para in enumerate(doc.paragraphs):
    if para.style and 'Heading 1' in para.style.name:
        text = para.text.strip()[:40]
        print(f'  {i}: {text}')
        
        # 检查是否有额外间距
        pf = para.paragraph_format
        if pf.space_before or pf.space_after or pf.line_spacing:
            print(f'      space_before={pf.space_before.pt if pf.space_before else "None"}')
            print(f'      space_after={pf.space_after.pt if pf.space_after else "None"}')
            print(f'      line_spacing={pf.line_spacing}')
