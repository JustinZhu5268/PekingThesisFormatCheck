# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')
from docx import Document
from emba_checker.rule_engine import RuleEngine
from emba_checker.zone_detector import detect_zones
import json

with open('D:/Projects/ThesisFormatCheck/emba_checker/rules_registry.json', 'r') as f:
    rules = json.load(f)

doc = Document('D:/Projects/ThesisFormatCheck/emba_checker/tests/test_full_compliant.docx')
zones = detect_zones(doc)

p_rules = [r for r in rules if r.get('target_group') == 'Group2_Paragraphs']
engine = RuleEngine(doc, p_rules, zones)
issues = engine.run_all()

# 找出 '规则未配置' 和 '其他' 的 info
infos = [i for i in issues if i.severity == 'info']

print('=== 规则未配置 (7个) ===')
for i in infos:
    if '未配置' in i.message:
        print(f'  {i.rule_id}: {i.message}')

print()
print('=== 其他 Info (20个) ===')
other = [i for i in infos if '未配置' not in i.message and '未找到' not in i.message and '通过' not in i.message]
for i in other:
    print(f'  {i.rule_id}: {i.message[:80]}')
