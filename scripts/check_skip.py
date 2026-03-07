# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')
import json

with open('D:/Projects/ThesisFormatCheck/emba_checker/rules_registry.json', 'r') as f:
    rules = json.load(f)

# 检查 20个被跳过的规则
skip_rules = [
    'TOC_05', 'HEADING_02', 'BODY_06', 'MISC_01', 'MISC_09', 'MISC_13',
    'MISC_20', 'MISC_21', 'EXPR_01', 'EXPR_03', 'EXPR_04', 'EXPR_05',
    'FOOT_05', 'FOOT_06', 'FOOT_07', 'APPENDIX_02', 'APPENDIX_03',
    'TEXT_NORM_08', 'TEXT_NORM_10', 'CONCLUSION_05'
]

print('=== 被跳过规则的详情 ===')
for r in rules:
    if r['rule_id'] in skip_rules:
        print(f"{r['rule_id']}: check_type={r.get('check_type')}, conditions={r.get('conditions', {})}")
