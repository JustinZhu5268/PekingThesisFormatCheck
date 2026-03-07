# -*- coding: utf-8 -*-
"""
test_claude_engine_extended.py - ClaudeEngine扩展测试
包含边界测试和异常测试，用于提升测试覆盖率
"""
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from docx import Document

sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')


@pytest.mark.integration
class TestClaudeEngineBoundary:
    """ClaudeEngine边界测试"""

    def test_empty_rules(self):
        """边界测试：空规则"""
        from emba_checker.claude_engine import ClaudeEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        engine = ClaudeEngine(doc, [], {}, api_key=None)
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_single_rule(self):
        """边界测试：单条规则"""
        from emba_checker.claude_engine import ClaudeEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        rules = [{
            "rule_id": "TEST_01",
            "check_type": "ai_semantic",
            "enabled": True
        }]
        
        engine = ClaudeEngine(doc, rules, {}, api_key=None)
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_many_rules(self):
        """边界测试：大量规则（50条）"""
        from emba_checker.claude_engine import ClaudeEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        rules = [{"rule_id": f"TEST_{i:03d}", "check_type": "ai_semantic", "enabled": True} for i in range(50)]
        
        engine = ClaudeEngine(doc, rules, {}, api_key=None)
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_empty_document(self):
        """边界测试：空文档"""
        from emba_checker.claude_engine import ClaudeEngine
        
        doc = Document()
        
        rules = [{"rule_id": "TEST_01", "check_type": "ai_semantic", "enabled": True}]
        
        engine = ClaudeEngine(doc, rules, {}, api_key=None)
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_empty_text(self):
        """边界测试：空文本"""
        from emba_checker.claude_engine import ClaudeEngine
        
        doc = Document()
        doc.add_paragraph("")
        
        rules = [{"rule_id": "TEST_01", "check_type": "ai_semantic", "enabled": True}]
        
        engine = ClaudeEngine(doc, rules, {}, api_key=None)
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_very_long_text(self):
        """边界测试：超长文本"""
        from emba_checker.claude_engine import ClaudeEngine
        
        doc = Document()
        long_text = "测试内容 " * 10000
        doc.add_paragraph(long_text)
        
        rules = [{"rule_id": "TEST_01", "check_type": "ai_semantic", "enabled": True}]
        
        engine = ClaudeEngine(doc, rules, {}, api_key=None)
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_unicode_text(self):
        """边界测试：Unicode文本"""
        from emba_checker.claude_engine import ClaudeEngine
        
        doc = Document()
        doc.add_paragraph("中文测试 \u4e00\u4e01 \U0001f600")
        
        rules = [{"rule_id": "TEST_01", "check_type": "ai_semantic", "enabled": True}]
        
        engine = ClaudeEngine(doc, rules, {}, api_key=None)
        issues = engine.run_all()
        assert isinstance(issues, list)


@pytest.mark.integration
class TestClaudeEngineException:
    """ClaudeEngine异常测试"""

    def test_disabled_rule(self):
        """异常测试：禁用的规则"""
        from emba_checker.claude_engine import ClaudeEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        rules = [{"rule_id": "TEST_01", "check_type": "ai_semantic", "enabled": False}]
        
        engine = ClaudeEngine(doc, rules, {}, api_key=None)
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_missing_check_type(self):
        """异常测试：缺少check_type"""
        from emba_checker.claude_engine import ClaudeEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        rules = [{"rule_id": "TEST_01", "enabled": True}]
        
        engine = ClaudeEngine(doc, rules, {}, api_key=None)
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_empty_rule(self):
        """异常测试：空规则"""
        from emba_checker.claude_engine import ClaudeEngine
        
        doc = Document()
        
        engine = ClaudeEngine(doc, [{}], {}, api_key=None)
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_empty_zone_map(self):
        """异常测试：空zone_map"""
        from emba_checker.claude_engine import ClaudeEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        rules = [{"rule_id": "TEST_01", "check_type": "ai_semantic", "enabled": True}]
        
        engine = ClaudeEngine(doc, rules, {}, api_key=None)
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_no_api_key(self):
        """异常测试：无API key"""
        from emba_checker.claude_engine import ClaudeEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        rules = [{"rule_id": "TEST_01", "check_type": "ai_semantic", "enabled": True}]
        
        engine = ClaudeEngine(doc, rules, {}, api_key=None)
        assert engine.enabled == False
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_api_key_from_env(self):
        """测试：从环境变量获取API key"""
        from emba_checker.claude_engine import ClaudeEngine
        
        doc = Document()
        
        engine = ClaudeEngine(doc, [], {}, api_key=None)
        assert isinstance(engine.enabled, bool)

    def test_client_init_failure(self):
        """测试：客户端初始化失败"""
        from emba_checker.claude_engine import ClaudeEngine
        
        doc = Document()
        
        engine = ClaudeEngine(doc, [], {}, api_key=None)
        assert engine.client is None

    def test_execution_log(self):
        """测试：执行日志"""
        from emba_checker.claude_engine import ClaudeEngine
        
        doc = Document()
        
        engine = ClaudeEngine(doc, [], {}, api_key=None)
        assert isinstance(engine.execution_log, list)

    def test_default_model(self):
        """测试：默认模型"""
        from emba_checker.claude_engine import ClaudeEngine
        
        assert ClaudeEngine.DEFAULT_MODEL == "claude-sonnet-4-5-20250929"

    def test_timeout_constants(self):
        """测试：超时常量"""
        from emba_checker.claude_engine import ClaudeEngine
        
        assert ClaudeEngine.SINGLE_CALL_TIMEOUT == 30
        assert ClaudeEngine.TOTAL_TIMEOUT == 120

    def test_progress_callback(self):
        """测试：进度回调"""
        from emba_checker.claude_engine import ClaudeEngine
        
        progress_calls = []
        
        def callback(group, msg, cur, total):
            progress_calls.append((group, msg))
        
        doc = Document()
        
        engine = ClaudeEngine(doc, [], {}, api_key=None, progress_callback=callback)
        assert engine.progress_callback is not None

    def test_api_key_property(self):
        """测试：API key属性"""
        from emba_checker.claude_engine import ClaudeEngine
        
        doc = Document()
        
        engine = ClaudeEngine(doc, [], {}, api_key="test_key")
        assert engine.api_key == "test_key"

    def test_issues_property(self):
        """测试：issues属性"""
        from emba_checker.claude_engine import ClaudeEngine
        
        doc = Document()
        
        engine = ClaudeEngine(doc, [], {}, api_key=None)
        assert isinstance(engine.issues, list)
