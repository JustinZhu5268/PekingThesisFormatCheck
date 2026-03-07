# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')
import json

with open('D:/Projects/ThesisFormatCheck/emba_checker/rules_registry.json', 'r') as f:
    rules = json.load(f)

# 找出 DECL_01-04 的 target_zone
for r in rules:
    if r['rule_id'].startswith('DECL_'):
        print(f"{r['rule_id']}: target_zone={r.get('target_zone', [])}")
