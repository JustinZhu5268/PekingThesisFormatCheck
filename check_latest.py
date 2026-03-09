# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

# Get latest file
import glob
import os

files = glob.glob('data/test_已修复_*.docx')
latest = max(files, key=os.path.getmtime)
print(f"Checking: {latest}")

doc = Document(latest)

print("\n" + "=" * 60)
print("Check paragraph 211 format (latest)")
print("=" * 60)

para = doc.paragraphs[211]
print(f"Para 211: {para.text[:60]}...")
for j, run in enumerate(para.runs[:3]):
    print(f"  Run {j}: bold={run.font.bold}, text: {run.text[:30]}")
