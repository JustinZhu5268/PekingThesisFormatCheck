# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

doc = Document('data/test_已修复_20260309_030133.docx')

print('Total sections:', len(doc.sections))
for i, s in enumerate(doc.sections):
    top = s.top_margin.pt if s.top_margin else 'N/A'
    header_dist = s.header_distance if hasattr(s, 'header_distance') else 'N/A'
    print(f'Section {i}: top_margin={top}pt, header_distance={header_dist}')
