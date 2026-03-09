# -*- coding: utf-8 -*-
"""检查致谢段落的字符"""
from docx import Document

doc = Document('data/test.docx')

# 段落 1201
para = doc.paragraphs[1201]
text = para.text.strip()

print(f"段落1201文本: '{text}'")
print(f"字符分析:")
for i, c in enumerate(text):
    print(f"  字符 {i}: '{c}' (U+{ord(c):04X})")

# 检查
print(f"\n是否等于'致谢': {text == '致谢'}")
print(f"是否等于'致谢  ' (带空格): {text == '致谢  '}")
print(f"startswith '致': {text.startswith('致')}")
