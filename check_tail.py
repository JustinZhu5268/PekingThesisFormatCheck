# -*- coding: utf-8 -*-
from docx import Document
import sys

doc = Document('data/test.docx')

print("查找包含'参考文献'/'附录'/'致谢'的段落:\n")
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if '参考文献' in text or '附录' in text or '致谢' in text:
        style = para.style.name if para.style else 'None'
        print(f"段落 {i}: [{style}] {text[:80]}")
