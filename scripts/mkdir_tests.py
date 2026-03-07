# -*- coding: utf-8 -*-
import os

dirs = [
    'D:/Projects/ThesisFormatCheck/emba_checker/tests/unit',
    'D:/Projects/ThesisFormatCheck/emba_checker/tests/integration',
    'D:/Projects/ThesisFormatCheck/emba_checker/tests/e2e',
    'D:/Projects/ThesisFormatCheck/emba_checker/tests/fixtures',
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
    print(f"Created: {d}")
