# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

doc = Document('data/test_已修复_20260309_094827.docx')

# 找到关键章节的位置
key_chapters = {}
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if text in ['参考文献', '附录', '致谢']:
        key_chapters[text] = i
        print(f'{text}: paragraph {i}')
    # 检查带"第X章"的
    if '第' in text and ('参考文献' in text or '附录' in text or ('致' in text and '谢' in text)):
        print(f'  Found: paragraph {i}: {text[:30]}')
