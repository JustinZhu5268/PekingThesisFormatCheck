# -*- coding: utf-8 -*-
"""Debug: 检查致谢为什么没有被处理"""
from docx import Document
from docx.oxml import OxmlElement

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

doc = Document('data/test.docx')

# 检查所有Heading 1段落的文本
print("所有Heading 1段落:")
for i, para in enumerate(doc.paragraphs):
    style_name = para.style.name if para.style else ""
    if 'Heading 1' in style_name:
        text = para.text.strip()
        # 只显示末尾几个
        if len(text) < 30:
            print(f"  段落 {i}: '{text}' (len={len(text)})")
            # 打印字符
            for j, c in enumerate(text):
                print(f"    char {j}: '{c}' U+{ord(c):04X}")
