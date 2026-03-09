# -*- coding: utf-8 -*-
"""检查致谢段落的详细信息"""
from docx import Document

doc = Document('data/test.docx')

# 段落 1201
para = doc.paragraphs[1201]
text = para.text
style_name = para.style.name if para.style else 'None'

print(f"段落 1201:")
print(f"  样式: {style_name}")
print(f"  文本: '{text}'")
print(f"  strip后: '{text.strip()}'")
print(f"  repr: {repr(text)}")
print(f"  strip repr: {repr(text.strip())}")

# 检查文本是否包含"致"
thanks_char = '\u81f4'
print(f"\n检查是否包含'致': {thanks_char in text}")
print(f"检查是否等于'致谢': {text.strip() == '致谢'}")
