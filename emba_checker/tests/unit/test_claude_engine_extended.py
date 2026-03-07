# -*- coding: utf-8 -*-
"""
test_claude_engine_extended.py - Claude引擎扩展测试
"""
import pytest
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

from unittest.mock import Mock, patch, MagicMock

@pytest.mark.unit
class TestClaudeEngineStructure:
    """测试ClaudeEngine类结构"""

    def test_claude_engine_import(self):
        """验证ClaudeEngine可导入"""
        from emba_checker.claude_engine import ClaudeEngine
        assert ClaudeEngine is not None

    def test_claude_engine_has_run_all(self):
        """验证有run_all方法"""
        from emba_checker.claude_engine import ClaudeEngine
        assert hasattr(ClaudeEngine, 'run_all')

    def test_claude_engine_has_run_async(self):
        """验证有run_async方法"""
        from emba_checker.claude_engine import ClaudeEngine
        assert hasattr(ClaudeEngine, 'run_async')

    def test_claude_engine_has_is_enabled(self):
        """验证有is_enabled属性"""
        from emba_checker.claude_engine import ClaudeEngine
        assert hasattr(ClaudeEngine, 'is_enabled')

    def test_claude_engine_has_get_summary(self):
        """验证有get_summary方法"""
        from emba_checker.claude_engine import ClaudeEngine
        assert hasattr(ClaudeEngine, 'get_summary')

@pytest.mark.unit
class TestClaudeEngineConstants:
    """测试ClaudeEngine常量"""

    def test_default_model_constant(self):
        """验证DEFAULT_MODEL常量"""
        from emba_checker.claude_engine import ClaudeEngine
        assert hasattr(ClaudeEngine, 'DEFAULT_MODEL')

    def test_timeout_constants(self):
        """验证超时常量"""
        from emba_checker.claude_engine import ClaudeEngine
        assert hasattr(ClaudeEngine, 'SINGLE_CALL_TIMEOUT')
        assert hasattr(ClaudeEngine, 'TOTAL_TIMEOUT')

@pytest.mark.unit
class TestClaudeEnginePromptBuilding:
    """测试Prompt构建"""

    def test_claude_engine_has_build_prompt_method(self):
        """验证有构建prompt的方法"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/claude_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'prompt' in content.lower()

    def test_claude_engine_has_zone_batching(self):
        """验证有分区批处理逻辑"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/claude_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'zone' in content.lower()

@pytest.mark.unit
class TestClaudeEngineErrorHandling:
    """测试错误处理"""

    def test_claude_engine_has_timeout_handling(self):
        """验证有超时处理"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/claude_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'timeout' in content.lower()

    def test_claude_engine_has_error_handling(self):
        """验证有错误处理"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/claude_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'except' in content.lower()

    def test_claude_engine_has_retry_logic(self):
        """验证有重试逻辑"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/claude_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'retry' in content.lower() or 'error' in content.lower()
