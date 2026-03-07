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

# 查看 _get_text_in_zones 的输出
p_rules = [r for r in rules if r['rule_id'] == 'DECL_01']
engine = RuleEngine(doc, p_rules, zones)

# 获取 declaration 区域的文本
text = engine._get_text_in_zones(['declaration'])
print(f'declaration 区域文本: {text[:200]}')
print(f'包含"收存": {"收存" in text}')
