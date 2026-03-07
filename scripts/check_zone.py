# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')
import json

with open('D:/Projects/ThesisFormatCheck/emba_checker/rules_registry.json', 'r') as f:
    rules = json.load(f)

# 找 DECL_01-04
print('=== Zone 配置问题 ===')
for r in rules:
    if r['rule_id'].startswith('DECL_') and r['rule_id'] in ['DECL_01', 'DECL_02', 'DECL_03', 'DECL_04']:
        print(f"{r['rule_id']}: target_zone={r.get('target_zone')}, check_type={r.get('check_type')}")

print()

# 检查 check_type=skip 但有非空 conditions 的规则
print('=== Skip 规则但有 conditions ===')
for r in rules:
    if r.get('check_type') == 'skip' and r.get('conditions'):
        print(f"{r['rule_id']}: conditions={r.get('conditions')}")
