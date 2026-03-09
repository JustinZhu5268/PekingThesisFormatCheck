# -*- coding: utf-8 -*-
import glob
import os
from docx import Document

# Check original test.docx
doc = Document(r'D:\Projects\ThesisFormatCheck\data\test.docx')

print("Checking test.docx for English keywords...")
for i, p in enumerate(doc.paragraphs):
    text = p.text.strip()
    text_lower = text.lower()
    
    # Print lines around "abstract" and "keywords"
    if 'abstract' in text_lower or 'keyword' in text_lower or 'key' in text_lower:
        print(f"Paragraph {i}: len={len(text)}, text={text[:80]}")
        print(f"  'abstract' in text_lower: {'abstract' in text_lower}")
        print(f"  'keyword' in text_lower: {'keyword' in text_lower}")
        print(f"  text_lower.startswith('key words'): {text_lower.startswith('key words')}")
        print()
