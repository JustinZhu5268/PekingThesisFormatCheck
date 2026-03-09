# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
from docx.shared import Pt

doc = Document('data/test_已修复_20260309_095405.docx')

print('Sections:', len(doc.sections))
for i, s in enumerate(doc.sections):
    print(f'\nSection {i}:')
    print(f'  top_margin: {s.top_margin.pt if s.top_margin else "N/A"} pt')
    print(f'  header_distance: {s.header_distance} EMU')
    if s.header_distance:
        print(f'  header_distance: {s.header_distance.pt} pt')
