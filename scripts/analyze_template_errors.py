# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')
import json
from docx import Document
from emba_checker.rule_engine import RuleEngine
from emba_checker.zone_detector import detect_zones

# 加载规则
with open('D:/Projects/ThesisFormatCheck/emba_checker/rules_registry.json', 'r', encoding='utf-8') as f:
    rules = json.load(f)

doc = Document('D:/Projects/ThesisFormatCheck/emba_checker/tests/test_complete_template.docx')
zones = detect_zones(doc)

# 运行所有规则
engine = RuleEngine(doc, rules, zones)
all_issues = engine.run_all()

errors = [i for i in all_issues if i.severity == 'error']
infos = [i for i in all_issues if i.severity == 'info']

print('=== 45个错误 ===')
for i in errors[:30]:
    print(f"{i.rule_id}: {i.message[:60]}")

print(f"\n=== 58个信息 ===")
for i in infos[:20]:
    print(f"{i.rule_id}: {i.message[:60]}")
