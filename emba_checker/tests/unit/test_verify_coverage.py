# -*- coding: utf-8 -*-
"""
test_verify_coverage.py - 覆盖率验证测试
"""
import pytest
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

@pytest.mark.unit
class TestVerifyCoverage:

    def test_verify_coverage_import(self):
        """验证覆盖率验证模块可导入"""
        from emba_checker.verify_coverage import verify_coverage
        assert verify_coverage is not None

    def test_md_keys_extraction(self):
        """验证MD键提取"""
        from emba_checker.verify_coverage import parse_md_keys
        keys = parse_md_keys('D:/Projects/ThesisFormatCheck/docs/EMBA论文格式排版要求清单完善版.md')
        assert len(keys) > 100

    def test_registry_keys_extraction(self):
        """验证规则库键提取"""
        from emba_checker.verify_coverage import parse_registry_keys
        keys = parse_registry_keys('D:/Projects/ThesisFormatCheck/emba_checker/rules_registry.json')
        assert len(keys) > 100
