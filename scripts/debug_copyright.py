# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')
from docx import Document
from emba_checker.zone_detector import detect_zones

doc = Document('D:/Projects/ThesisFormatCheck/emba_checker/tests/test_full_compliant.docx')
zones = detect_zones(doc)

# 查看 copyright 区域
text = ''
for i, p in enumerate(doc.paragraphs):
    if zones.get(i) == 'copyright':
        text += p.text + ' '

print(f'copyright 区域文本: {text[:200]}')
print(f'包含"收存": {"收存" in text}')
