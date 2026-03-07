# -*- coding: utf-8 -*-
"""
test_safe_annotator_extended.py - SafeAnnotator扩展测试
"""
import pytest
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

@pytest.mark.unit
class TestSafeAnnotatorStructure:
    """测试SafeAnnotator类结构"""

    def test_safe_annotator_import(self):
        """验证SafeAnnotator可导入"""
        from emba_checker.safe_annotator import SafeAnnotator
        assert SafeAnnotator is not None

    def test_safe_annotator_has_init(self):
        """验证有初始化方法"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/safe_annotator.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'def __init__' in content

    def test_safe_annotator_has_annotate_all(self):
        """验证有annotate_all方法"""
        from emba_checker.safe_annotator import SafeAnnotator
        assert hasattr(SafeAnnotator, 'annotate_all')

    def test_safe_annotator_has_save(self):
        """验证有save方法"""
        from emba_checker.safe_annotator import SafeAnnotator
        assert hasattr(SafeAnnotator, 'save')

    def test_safe_annotator_has_get_log(self):
        """验证有get_log方法"""
        from emba_checker.safe_annotator import SafeAnnotator
        assert hasattr(SafeAnnotator, 'get_log')

@pytest.mark.unit
class TestSafeAnnotatorAnnotation:
    """测试SafeAnnotator标注功能"""

    def test_safe_annotator_has_annotation_colors(self):
        """验证有标注颜色"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/safe_annotator.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'RGBColor' in content or 'WD_COLOR_INDEX' in content

    def test_safe_annotator_has_font_settings(self):
        """验证有字体设置"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/safe_annotator.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'font' in content.lower()

    def test_safe_annotator_has_highlight(self):
        """验证有高亮功能"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/safe_annotator.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'HIGHLIGHT' in content or 'highlight' in content.lower()

    def test_safe_annotator_has_annotation_method(self):
        """验证有标注方法"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/safe_annotator.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert '_annotate_' in content

@pytest.mark.unit
class TestSafeAnnotatorConstants:
    """测试SafeAnnotator常量"""

    def test_safe_annotator_has_font_size_constant(self):
        """验证有字体大小常量"""
        from emba_checker.safe_annotator import SafeAnnotator
        assert hasattr(SafeAnnotator, 'ANNOTATION_FONT_SIZE')

    def test_safe_annotator_has_font_color_constant(self):
        """验证有字体颜色常量"""
        from emba_checker.safe_annotator import SafeAnnotator
        assert hasattr(SafeAnnotator, 'ANNOTATION_FONT_COLOR')

    def test_safe_annotator_has_font_bold_constant(self):
        """验证有字体粗细常量"""
        from emba_checker.safe_annotator import SafeAnnotator
        assert hasattr(SafeAnnotator, 'ANNOTATION_FONT_BOLD')

    def test_safe_annotator_has_highlight_color_constant(self):
        """验证有高亮颜色常量"""
        from emba_checker.safe_annotator import SafeAnnotator
        assert hasattr(SafeAnnotator, 'HIGHLIGHT_COLOR')
