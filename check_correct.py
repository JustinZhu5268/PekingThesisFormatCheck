# -*- coding: utf-8 -*-
import os, re
from docx import Document

files = [f for f in os.listdir('data') if f.startswith('test_') and f.endswith('.docx') and '备份' not in f]
files.sort(key=lambda x: os.path.getmtime(os.path.join('data', x)), reverse=True)
doc = Document(os.path.join('data', files[0]))

print('Checking for CORRECT heading pattern issues...\n')

issues = []
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    # CORRECT pattern: 1.1 xxx (level 2), 1.1.1 xxx (level 3)
    # WRONG pattern: 1.1. xxx or 1.1.1. xxx (extra dot before space)
    
    # Check for "X.X. xxx" pattern (level 2 with extra dot)
    if re.match(r'^\d+\.\d+\.\s', text):
        issues.append((i, text[:60], 'level-2'))
    # Check for "X.X.X. xxx" pattern (level 3 with extra dot)  
    elif re.match(r'^\d+\.\d+\.\d+\.\s', text):
        issues.append((i, text[:60], 'level-3'))

print(f'Total issues found: {len(issues)}\n')
for idx, txt, level in issues[:40]:
    print(f'Para {idx} ({level}): {txt}')
