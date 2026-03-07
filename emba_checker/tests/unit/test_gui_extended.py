# -*- coding: utf-8 -*-
"""
test_gui_extended.py - GUI模块扩展测试
"""
import pytest
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

@pytest.mark.unit
class TestGUIClassStructure:
    """测试GUI类结构"""

    def test_gui_class_exists(self):
        """验证GUI类存在"""
        import importlib.util
        spec = importlib.util.find_spec('emba_checker.gui')
        assert spec is not None

    def test_gui_class_name(self):
        """验证GUI类名"""
        import os
        gui_path = os.path.join('D:/Projects/ThesisFormatCheck/emba_checker/gui.py')
        with open(gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'EMBAcheckerGUI' in content

@pytest.mark.unit
class TestGUIMethods:
    """测试GUI方法"""

    def test_gui_has_init_method(self):
        """验证__init__方法存在"""
        import os
        gui_path = os.path.join('D:/Projects/ThesisFormatCheck/emba_checker/gui.py')
        with open(gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert '__init__' in content

    def test_gui_has_select_doc_method(self):
        """验证select_doc方法存在"""
        import os
        gui_path = os.path.join('D:/Projects/ThesisFormatCheck/emba_checker/gui.py')
        with open(gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert '_select_doc_file' in content

    def test_gui_has_select_rules_method(self):
        """验证select_rules方法存在"""
        import os
        gui_path = os.path.join('D:/Projects/ThesisFormatCheck/emba_checker/gui.py')
        with open(gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert '_select_rules_file' in content

    def test_gui_has_start_check(self):
        """验证start_check方法存在"""
        import os
        gui_path = os.path.join('D:/Projects/ThesisFormatCheck/emba_checker/gui.py')
        with open(gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert '_start_check' in content

    def test_gui_has_update_progress(self):
        """验证update_progress方法存在"""
        import os
        gui_path = os.path.join('D:/Projects/ThesisFormatCheck/emba_checker/gui.py')
        with open(gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'update_progress' in content

    def test_gui_has_log_method(self):
        """验证log方法存在"""
        import os
        gui_path = os.path.join('D:/Projects/ThesisFormatCheck/emba_checker/gui.py')
        with open(gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'def _log' in content

    def test_gui_has_result_method(self):
        """验证result方法存在"""
        import os
        gui_path = os.path.join('D:/Projects/ThesisFormatCheck/emba_checker/gui.py')
        with open(gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert '_update_summary' in content

    def test_gui_has_open_method(self):
        """验证open方法存在"""
        import os
        gui_path = os.path.join('D:/Projects/ThesisFormatCheck/emba_checker/gui.py')
        with open(gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert '_open_docx' in content or '_open_report' in content

@pytest.mark.unit
class TestGUIComponents:
    """测试GUI组件"""

    def test_gui_has_threading(self):
        """验证使用了threading"""
        import os
        gui_path = os.path.join('D:/Projects/ThesisFormatCheck/emba_checker/gui.py')
        with open(gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'threading' in content

    def test_gui_has_filedialog(self):
        """验证使用了filedialog"""
        import os
        gui_path = os.path.join('D:/Projects/ThesisFormatCheck/emba_checker/gui.py')
        with open(gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'filedialog' in content

    def test_gui_has_messagebox(self):
        """验证使用了messagebox"""
        import os
        gui_path = os.path.join('D:/Projects/ThesisFormatCheck/emba_checker/gui.py')
        with open(gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'messagebox' in content

    def test_gui_has_queue(self):
        """验证使用了queue"""
        import os
        gui_path = os.path.join('D:/Projects/ThesisFormatCheck/emba_checker/gui.py')
        with open(gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'queue' in content

@pytest.mark.unit
class TestGUIVariables:
    """测试GUI变量"""

    def test_gui_has_doc_path_var(self):
        """验证有doc_path变量"""
        import os
        gui_path = os.path.join('D:/Projects/ThesisFormatCheck/emba_checker/gui.py')
        with open(gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'self.doc_path' in content

    def test_gui_has_rules_path_var(self):
        """验证有rules_path变量"""
        import os
        gui_path = os.path.join('D:/Projects/ThesisFormatCheck/emba_checker/gui.py')
        with open(gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'self.rules_path' in content

    def test_gui_has_check_level_var(self):
        """验证有check_level变量"""
        import os
        gui_path = os.path.join('D:/Projects/ThesisFormatCheck/emba_checker/gui.py')
        with open(gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'self.check_level' in content

    def test_gui_has_enable_ai_var(self):
        """验证有enable_ai变量"""
        import os
        gui_path = os.path.join('D:/Projects/ThesisFormatCheck/emba_checker/gui.py')
        with open(gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'self.enable_ai' in content
