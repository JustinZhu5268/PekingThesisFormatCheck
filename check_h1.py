# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

doc = Document('data/test_已修复_20260309_094827.docx')

# 找到所有Heading 1的段落
print('Heading 1 paragraphs:')
for i, para in enumerate(doc.paragraphs):
    if para.style and 'Heading 1' in para.style.name:
        print(f'  {i}: {para.text[:50]}')
