# -*- coding: utf-8 -*-
import os
files = [f for f in os.listdir('data') if 'test_' in f and f.endswith('.docx')]
for f in sorted(files, key=lambda x: os.path.getmtime(os.path.join('data', x)), reverse=True)[:8]:
    print(f)
