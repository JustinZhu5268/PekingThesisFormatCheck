# -*- coding: utf-8 -*-
"""测试参考文献修复功能"""
import json
from emba_checker.docx_autofixer import DocxAutoFixer

# 加载规则
with open('emba_checker/rules_registry.json', 'r', encoding='utf-8') as f:
    rules = json.load(f)

# 使用test3.docx
fixer = DocxAutoFixer('data/test3.docx', rules, backup=False)
fixer.fix_references_and_citations()
fixer.doc.save('data/test_refs_fixed.docx')
print("修复完成，保存到 test_refs_fixed.docx")
