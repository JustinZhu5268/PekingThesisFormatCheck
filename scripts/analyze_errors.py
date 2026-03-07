# -*- coding: utf-8 -*-
"""
分析45个错误的来源
"""
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

# 按规则ID分类
error_by_rule = {}
for i in errors:
    if i.rule_id not in error_by_rule:
        error_by_rule[i.rule_id] = []
    error_by_rule[i.rule_id].append(i)

print("=== 45个错误按规则分类 ===")
print(f"共 {len(error_by_rule)} 个规则报错\n")

# 分析每个规则的错误原因
for rule_id, issues in sorted(error_by_rule.items()):
    # 找到规则详情
    rule = next((r for r in rules if r['rule_id'] == rule_id), None)
    if rule:
        check_type = rule.get('check_type', 'unknown')
        conditions = rule.get('conditions', {})
        print(f"【{rule_id}】({check_type})")
        print(f"  conditions: {conditions}")
        print(f"  错误数: {len(issues)}")
        print(f"  样例: {issues[0].message[:80]}")
        print()
