# -*- coding: utf-8 -*-
import os, re
from docx import Document

files = [f for f in os.listdir('data') if f.startswith('test_') and f.endswith('.docx') and '备份' not in f]
files.sort(key=lambda x: os.path.getmtime(os.path.join('data', x)), reverse=True)
doc = Document(os.path.join('data', files[0]))

print('Checking ENTIRE document for heading issues...\n')

issues = []
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    # Match: 1.1. xxx or 1.1.1. xxx (two dots minimum, then space)
    if re.match(r'^\d+\.\d+\.', text):
        # Check if there's a space after the number pattern
        m = re.match(r'^(\d+\.)+', text)
        if m:
            prefix = m.group(0)
            # Count the dots in prefix
            dot_count = prefix.count('.')
            if dot_count >= 2:
                issues.append((i, text[:60]))

print(f'Total issues found: {len(issues)}\n')
for idx, txt in issues[:30]:
    print(f'Para {idx}: {txt}')
