# -*- coding: utf-8 -*-
import glob
import re
from docx import Document

# 找到修复后的文件
files = glob.glob(r'D:\Projects\ThesisFormatCheck\data\test_已修复_*.docx')
files = [f for f in files if '备份' not in f]
latest = max(files, key=lambda x: x)
print('File:', latest)

doc = Document(latest)

# 检查具体标题格式
print('\n=== 检查三级标题格式 ===')
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    # 查找类似 "1.1 1." 这种错误格式
    if re.match(r'^\d+\.\d+\s+\d+\.', text):
        print('错误格式段落{}: {}'.format(i, text[:60]))
    # 查找正确格式
    if re.match(r'^\d+\.\d+\.\d+\s+', text):
        print('正确格式段落{}: {}'.format(i, text[:60]))
