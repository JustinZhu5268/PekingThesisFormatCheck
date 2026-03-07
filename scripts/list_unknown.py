# -*- coding: utf-8 -*-
import json

with open(r'D:\Projects\ThesisFormatCheck\emba_checker\rules_registry.json', 'r', encoding='utf-8') as f:
    rules = json.load(f)

unknown = [r for r in rules if r.get('check_type') == 'unknown' or r.get('conditions', {}).get('_needs_manual_review')]
print(f'需人工补全: {len(unknown)} 条\n')

# 按 md_source 分组
from collections import defaultdict
groups = defaultdict(list)
for r in unknown:
    groups[r.get('md_source', 'Unknown')].append(r)

for section, rs in sorted(groups.items()):
    print(f'## {section}')
    for r in rs:
        print(f'  - {r["rule_id"]}: {r["element_name"]}')
        print(f'    check_type: {r["check_type"]}')
        print(f'    raw: {r["conditions"]}')
    print()
