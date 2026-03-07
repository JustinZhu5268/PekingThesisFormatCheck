# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')
from docx import Document
from emba_checker.zone_detector import detect_zones

doc = Document('D:/Projects/ThesisFormatCheck/emba_checker/tests/test_full_compliant.docx')
zones = detect_zones(doc)

# 查看每个段落索引对应的 zone
print('段落 0-20 的 zone:')
for i in range(20):
    print(f'  [{i}] {doc.paragraphs[i].text[:30]} -> {zones.get(i, "unknown")}')
