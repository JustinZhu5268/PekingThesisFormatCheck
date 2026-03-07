# -*- coding: utf-8 -*-
"""
test_safe_annotator.py - 安全标注测试
"""
import pytest
import sys
import os
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

import tempfile

from docx import Document

@pytest.mark.integration
class TestSafeAnnotator:

    def test_safe_annotator_import(self):
        """验证SafeAnnotator可导入"""
        from emba_checker.safe_annotator import SafeAnnotator
        assert SafeAnnotator is not None

    def test_safe_annotator_methods(self):
        """验证SafeAnnotator类有正确的方法"""
        from emba_checker.safe_annotator import SafeAnnotator
        # SafeAnnotator有annotate_all和save方法
        assert hasattr(SafeAnnotator, 'annotate_all')
        assert hasattr(SafeAnnotator, 'save')
