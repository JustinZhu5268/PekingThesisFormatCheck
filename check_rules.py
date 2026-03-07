# -*- coding: utf-8 -*-
import json
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

with open('emba_checker/rules_registry.json', 'r', encoding='utf-8') as f:
    rules = json.load(f)

# 找出所有 target_zone 包含 body_chapter 的规则
body_rules = [r for r in rules if 'body_chapter' in r.get('target_zone', [])]

print(f"找到 {len(body_rules)} 条针对 body_chapter 的规则:\n")

for r in body_rules[:10]:
    print(f"规则: {r.get('rule_id')}")
    print(f"  元素: {r.get('element_name')}")
    print(f"  目标区域: {r.get('target_zone')}")
    print(f"  条件: {r.get('conditions')}")
    print()
