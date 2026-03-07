# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')
from docx import Document
from emba_checker.zone_detector import detect_zones

doc = Document('D:/Projects/ThesisFormatCheck/emba_checker/tests/test_full_compliant.docx')
zones = detect_zones(doc)

# 查看 declaration 区域
print('=== declaration 区域 ===')
for i, p in enumerate(doc.paragraphs):
    if zones.get(i) == 'declaration':
        print(f'[{i}] {p.text[:50]}')
