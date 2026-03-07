# -*- coding: utf-8 -*-
"""
test_claude_engine.py - Claude引擎测试
"""
import pytest
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

@pytest.mark.integration
class TestClaudeEngine:

    def test_claude_engine_import(self):
        """验证ClaudeEngine可导入"""
        from emba_checker.claude_engine import ClaudeEngine
        assert ClaudeEngine is not None

    def test_claude_engine_methods(self):
        """验证ClaudeEngine类有正确的方法"""
        from emba_checker.claude_engine import ClaudeEngine
        # ClaudeEngine有run_all和is_enabled方法
        assert hasattr(ClaudeEngine, 'run_all')
        assert hasattr(ClaudeEngine, 'is_enabled')
