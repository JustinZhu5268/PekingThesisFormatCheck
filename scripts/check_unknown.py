import json
with open(r'D:\Projects\ThesisFormatCheck\emba_checker\rules_registry.json', 'r', encoding='utf-8') as f:
    rules = json.load(f)
unknown = [r for r in rules if r.get('check_type') == 'unknown' or r.get('conditions', {}).get('_needs_manual_review')]
print(f'剩余需人工: {len(unknown)} 条')
for r in unknown:
    print(f'  {r["rule_id"]}: {r["element_name"]}')
