# -*- coding: utf-8 -*-
import sys
import re
from docx import Document

# 检查原始文件
doc = Document(r'D:\Projects\ThesisFormatCheck\data\test_已修复_20260307_200914_原文件备份.docx')
print('=== 原始文件中的图表引用 (旧格式) ===')
count = 0
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    # 查找图2-1, 表3-1 等
    matches = re.findall(r'[图表]\d+-\d+', text)
    if matches:
        print(f'段落 {i}: {matches}')
        count += 1
print(f'总数: {count}')
