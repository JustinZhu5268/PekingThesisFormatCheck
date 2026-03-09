# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
from docx.shared import Pt

# 使用刚修复的文件
import os
files = [f for f in os.listdir('data') if f.startswith('test_已修复') and f.endswith('.docx')]
files.sort(key=lambda x: os.path.getmtime(f'data/{x}'), reverse=True)
latest = files[0]
print(f'Checking: {latest}')

doc = Document(f'data/{latest}')

# 检查附录和致谢的格式
print('\n=== Checking appendix and acknowledgment spacing ===')
for i, para in enumerate(doc.paragraphs):
    if para.style and 'Heading 1' in para.style.name:
        text = para.text.strip()
        if text.startswith('附录') or '致谢' in text:
            pf = para.paragraph_format
            print(f'\n{text[:30]} (para {i}):')
            print(f'  space_before: {pf.space_before.pt if pf.space_before else "None"}')
            print(f'  space_after: {pf.space_after.pt if pf.space_after else "None"}')
            print(f'  line_spacing: {pf.line_spacing}')
            print(f'  line_spacing_rule: {pf.line_spacing_rule}')
