# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')
import json

# 加载规则
with open('D:/Projects/ThesisFormatCheck/emba_checker/rules_registry.json', 'r', encoding='utf-8') as f:
    rules = json.load(f)

# 统计修复的规则
fixed_rules = [
    'TOC_05', 'HEADING_02', 'BODY_06', 'MISC_01', 'MISC_09',
    'EXPR_01', 'EXPR_03', 'EXPR_04', 'EXPR_05',
    'APPENDIX_02', 'APPENDIX_03', 'TEXT_NORM_10',
    'MISC_13', 'MISC_20', 'MISC_21', 'FOOT_05', 'FOOT_06', 'FOOT_07'
]

print('=== 修复规则的 check_type ===')
for r in rules:
    if r['rule_id'] in fixed_rules:
        print(f"{r['rule_id']}: check_type={r['check_type']}, conditions={r.get('conditions', {})}")
