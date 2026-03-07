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

# 按规则ID分类，统计
error_by_rule = {}
for i in errors:
    if i.rule_id not in error_by_rule:
        error_by_rule[i.rule_id] = {'count': 0, 'message': i.message[:80]}
    error_by_rule[i.rule_id]['count'] += 1

print("=== 新模板错误统计 ===")
for rule_id, info in sorted(error_by_rule.items()):
    print(f"{rule_id}: {info['count']}处 - {info['message'][:60]}")
