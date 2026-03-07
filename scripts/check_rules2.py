# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')
import json

with open('D:/Projects/ThesisFormatCheck/emba_checker/rules_registry.json', 'r') as f:
    rules = json.load(f)

# 找出这些规则的 target_zone
for r in rules:
    if r['rule_id'] in ['COVER_06', 'DECL_01', 'DECL_02', 'DECL_03', 'DECL_04', 'MISC_06']:
        print(f"{r['rule_id']}: target_zone={r.get('target_zone', [])}, target_group={r.get('target_group', [])}")
