# -*- coding: utf-8 -*-
from docx import Document

doc = Document('data/test.docx')

print("查找'致谢'相关段落:\n")
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if '致谢' in text:
        style = para.style.name if para.style else 'None'
        print(f"段落 {i}: [{style}] '{text}'")
