# -*- coding: utf-8 -*-
from docx import Document

doc = Document('data/test.docx')

# 段落 179 和 180
for i in [179, 180]:
    para = doc.paragraphs[i]
    text = para.text
    print(f"段落 {i}:")
    print(f"  原始文本: '{text}'")
    print(f"  样式: {para.style.name if para.style else 'None'}")
    print(f"  strip后: '{text.strip()}'")
    print()
