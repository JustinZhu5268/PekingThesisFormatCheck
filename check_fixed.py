# -*- coding: utf-8 -*-
from docx import Document

# 检查修复后的文档
doc = Document('data/test_已修复_20260308_175420.docx')

print("修复后文档中包含'参考文献'/'附录'/'致谢'的段落:\n")
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if '参考文献' in text or '附录' in text or '致谢' in text:
        style = para.style.name if para.style else 'None'
        print(f"段落 {i}: [{style}] {text[:80]}")
