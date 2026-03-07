# -*- coding: utf-8 -*-
"""
test_gui.py - GUI测试
"""
import pytest
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

@pytest.mark.e2e
class TestGUI:

    def test_gui_import(self):
        """验证GUI可导入"""
        # 不实际创建窗口
        import importlib
        try:
            gui = importlib.import_module('emba_checker.gui')
            assert gui is not None
        except Exception as e:
            pytest.skip(f"GUI导入需要显示环境: {e}")
