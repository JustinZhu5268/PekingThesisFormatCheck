# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import glob
import os

# Get latest file
files = glob.glob('data/test_已修复_*.docx')
latest = max(files, key=os.path.getmtime)
print(f"Checking: {latest}\n")

# Check TOC field code
from docx import Document
import re

doc = Document(latest)

print("=" * 60)
print("Check TOC field codes")
print("=" * 60)

from docx.oxml.ns import qn

# Check instrText nodes
for instrText in doc.element.xpath('//w:instrText'):
    if instrText.text and 'TOC' in instrText.text:
        print(f"TOC field code: {instrText.text}")

# Check updateFields setting
print("\n" + "=" * 60)
print("Check updateFields setting")
print("=" * 60)

settings = doc.settings.element
updateFields = settings.find(qn('w:updateFields'))
if updateFields is not None:
    val = updateFields.get(qn('w:val'))
    print(f"updateFields w:val = {val}")
else:
    print("updateFields not found")

print("\nDone")
