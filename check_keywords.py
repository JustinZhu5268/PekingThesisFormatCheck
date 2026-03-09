# -*- coding: utf-8 -*-
import glob
import os
from docx import Document

# Find the fixed file
data_dir = r'D:\Projects\ThesisFormatCheck\data'
files = glob.glob(os.path.join(data_dir, '*.docx'))

for f in files:
    if 'test_已修复' in f and '备份' not in f:
        print(f"File: {os.path.basename(f)}")
        try:
            doc = Document(f)
            for i, p in enumerate(doc.paragraphs):
                text = p.text.strip()
                if 'keyword' in text.lower() or 'KEY' in text:
                    print(f"  Paragraph {i} (len={len(text)}): {text}")
        except Exception as e:
            print(f"  Error: {e}")

