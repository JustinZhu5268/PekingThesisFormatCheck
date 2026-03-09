# -*- coding: utf-8 -*-
from docx import Document

doc = Document('data/test.docx')

print("查找所有包含'第X章 参考文献/附录/致谢'的段落:\n")
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    style = para.style.name if para.style else 'None'
    if '参考文献' in text or '附录' in text or '致谢' in text:
        if '第' in text and '章' in text:
            print(f"段落 {i}: [{style}] '{text[:80]}'")
