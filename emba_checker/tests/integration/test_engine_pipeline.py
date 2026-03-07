# -*- coding: utf-8 -*-
"""
test_engine_pipeline.py - 引擎管线集成测试
"""
import pytest
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

from emba_checker.zone_detector import detect_zones
from emba_checker.rule_engine import RuleEngine

@pytest.mark.integration
class TestEnginePipeline:

    def test_error_doc_triggers_issues(self, error_doc, sample_rules):
        zone_map = detect_zones(error_doc)
        engine = RuleEngine(error_doc, sample_rules, zone_map)
        issues = engine.run_all()
        assert len(issues) > 0

    def test_sample_rules_loaded(self, sample_rules):
        assert len(sample_rules) == 5
        assert all(r.get("enabled") for r in sample_rules)
