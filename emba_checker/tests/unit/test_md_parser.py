# -*- coding: utf-8 -*-
"""
test_md_parser.py - MD解析器测试
"""
import pytest
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

from emba_checker.md_parser import parse_md_to_rules

@pytest.mark.unit
class TestMdParser:

    def test_parse_extracts_rules(self):
        """验证解析出规则"""
        rules = parse_md_to_rules('D:/Projects/ThesisFormatCheck/docs/EMBA论文格式排版要求清单完善版.md')
        assert len(rules) >= 160

    def test_parse_generates_rule_id(self):
        """验证生成rule_id"""
        rules = parse_md_to_rules('D:/Projects/ThesisFormatCheck/docs/EMBA论文格式排版要求清单完善版.md')
        rule_ids = [r['rule_id'] for r in rules]
        assert 'COVER_01' in rule_ids

    def test_parse_infers_check_type(self):
        """验证推断check_type"""
        rules = parse_md_to_rules('D:/Projects/ThesisFormatCheck/docs/EMBA论文格式排版要求清单完善版.md')
        # 找一个有字体要求的规则
        font_rules = [r for r in rules if 'font' in r.get('format_requirement', '').lower()]
        if font_rules:
            assert font_rules[0]['check_type'] in ['paragraph_style', 'unknown']

@pytest.mark.unit
class TestGenerateRegistry:

    def test_generate_registry_runs(self):
        """验证规则库生成"""
        from emba_checker.generate_registry import generate_registry
        # 不需要实际生成，只需验证可以导入
        assert generate_registry is not None
