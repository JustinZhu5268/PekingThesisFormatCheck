# -*- coding: utf-8 -*-
"""检查致谢在原始文档中的位置"""
from docx import Document
import sys

doc = Document('data/test.docx')

# 用Unicode码点来查找
thanks_char = '\u803e'  # 致谢的"谢"

print("查找包含'谢'字的段落:")
found = False
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    style_name = para.style.name if para.style else 'None'
    if thanks_char in text:
        found = True
        print(f"段落 {i}: [{style_name}] '{text[:50]}'")

if not found:
    print("未找到包含'谢'字的段落")
    
# 也搜索Heading 1
print("\n所有Heading 1段落（末尾5个）:")
heading1_list = []
for i, para in enumerate(doc.paragraphs):
    style_name = para.style.name if para.style else ""
    if 'Heading 1' in style_name:
        heading1_list.append((i, para.text.strip()[:40]))

for idx, (para_num, text) in enumerate(heading1_list[-5:]):
    print(f"段落 {para_num}: {text}")
