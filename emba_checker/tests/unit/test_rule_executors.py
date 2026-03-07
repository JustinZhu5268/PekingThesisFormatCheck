# -*- coding: utf-8 -*-
"""
test_rule_executors.py - 执行器测试
通过 RuleEngine 间接测试
"""
import pytest
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

from docx import Document
from docx.shared import Pt
from emba_checker.rule_engine import RuleEngine

@pytest.mark.unit
class TestRuleExecutorsViaEngine:
    """通过 RuleEngine 测试执行器"""

    def test_paragraph_style_executor(self):
        """测试 paragraph_style 执行器 - 通过时返回 info"""
        doc = Document()
        p = doc.add_paragraph()
        run = p.add_run("测试文本")
        run.font.name = "宋体"
        run.font.size = Pt(12)
        
        rule = {
            "rule_id": "TEST_01",
            "check_type": "paragraph_style",
            "target_group": "Group2_Paragraphs",
            "target_zone": ["cover"],
            "conditions": {"font_name_cn": "宋体", "font_size_pt": 12}
        }
        
        engine = RuleEngine(doc, [rule], {0: "cover"})
        issues = engine.run_all()
        
        # 通过时返回 info 级别的问题
        assert len(issues) == 1
        assert issues[0].severity == "info"

    def test_regex_match_executor(self):
        """测试 regex_match 执行器"""
        doc = Document()
        p = doc.add_paragraph("本研究发现，结果显著")  # 中文逗号
        
        rule = {
            "rule_id": "TEST_02",
            "check_type": "regex_match",
            "target_group": "Group2_Paragraphs",
            "target_zone": ["cover"],
            "conditions": {"pattern": ",", "match_mode": "must_not_match"}
        }
        
        engine = RuleEngine(doc, [rule], {0: "cover"})
        issues = engine.run_all()
        
        # 应该失败（发现英文逗号）
        assert len(issues) >= 1

    def test_count_check_executor(self):
        """测试 count_check 执行器"""
        doc = Document()
        p = doc.add_paragraph("字" * 100)  # 100个字符
        
        rule = {
            "rule_id": "TEST_03",
            "check_type": "count_check",
            "target_group": "Group2_Paragraphs",
            "target_zone": ["cover"],
            "conditions": {"count_type": "chinese_chars", "min_value": 200}
        }
        
        engine = RuleEngine(doc, [rule], {0: "cover"})
        issues = engine.run_all()
        
        # 应该失败（字数不足）
        assert len(issues) >= 1

    def test_forbidden_words_executor(self):
        """测试 forbidden_words 执行器"""
        doc = Document()
        p = doc.add_paragraph("我认为这个结论是正确的")
        
        rule = {
            "rule_id": "TEST_04",
            "check_type": "forbidden_words",
            "target_group": "Group2_Paragraphs",
            "target_zone": ["cover"],
            "conditions": {"inline_words": ["我认为"], "match_mode": "any"}
        }
        
        engine = RuleEngine(doc, [rule], {0: "cover"})
        issues = engine.run_all()
        
        # 应该失败（发现禁用词）
        assert len(issues) >= 1
