# -*- coding: utf-8 -*-
"""检查参考文献段落的样式"""
import sys
sys.path.insert(0, '.')

from docx import Document

# 查找参考文献
doc = Document('data/test.docx')

in_ref = False
ref_count = 0
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    
    # 检测参考文献开始
    if text == "参考文献":
        in_ref = True
        print(f"段落 {i}: 参考文献标题, 样式: {para.style.name}")
        continue
    
    if not in_ref:
        continue
    
    # 检测参考文献条目
    if text.startswith('['):
        ref_count += 1
        if ref_count <= 3:  # 只显示前3条
            print(f"段落 {i}: {text[:50]}, 样式: {para.style.name}")
        
    if ref_count >= 3:
        break
