# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
doc = Document('data/test_已修复_20260309_004116.docx')

print("=" * 60)
print("Check paragraph 211 format")
print("=" * 60)

para = doc.paragraphs[211]
print(f"Para 211: {para.text[:80]}")
for j, run in enumerate(para.runs):
    print(f"  Run {j}: bold={run.font.bold}, text: {run.text[:30]}")
