# -*- coding: utf-8 -*-
"""检查致谢在原始文档中的位置"""
from docx import Document

doc = Document('data/test.docx')

print("查找'致谢'段落:")
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    style_name = para.style.name if para.style else 'None'
    if '致谢' in text:
        print(f"段落 {i}: [{style_name}] '{text[:50]}'")
