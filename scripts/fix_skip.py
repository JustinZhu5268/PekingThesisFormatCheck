# -*- coding: utf-8 -*-
import json

with open('D:/Projects/ThesisFormatCheck/emba_checker/manual_overrides.json', 'r', encoding='utf-8') as f:
    overrides = json.load(f)

# 找出 check_type=skip 但有非空 conditions 的规则
fixed = 0
for o in overrides:
    if o.get('check_type') == 'skip' and o.get('conditions'):
        old = o.get('conditions')
        o['conditions'] = {}
        print(f"  {o['rule_id']}: {old} -> {{}}")
        fixed += 1

print(f'共修复 {fixed} 条')

with open('D:/Projects/ThesisFormatCheck/emba_checker/manual_overrides.json', 'w', encoding='utf-8') as f:
    json.dump(overrides, f, ensure_ascii=False, indent=2)

print('已保存')
