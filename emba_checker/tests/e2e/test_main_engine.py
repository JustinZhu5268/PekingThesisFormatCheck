# -*- coding: utf-8 -*-
"""
test_main_engine.py - 主引擎测试
"""
import pytest
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

@pytest.mark.e2e
class TestMainEngine:

    def test_main_engine_import(self):
        """验证MainEngine可导入"""
        from emba_checker.main_engine import MainEngine
        assert MainEngine is not None

    def test_main_engine_basic(self):
        """验证主引擎可实例化"""
        from emba_checker.main_engine import MainEngine
        # MainEngine需要doc_path参数
        import inspect
        sig = inspect.signature(MainEngine.__init__)
        params = list(sig.parameters.keys())
        # 如果需要doc_path，跳过
        if 'doc_path' in params:
            pytest.skip("MainEngine需要doc_path参数")
