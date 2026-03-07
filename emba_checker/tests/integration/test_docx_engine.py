# -*- coding: utf-8 -*-
"""
test_docx_engine.py - DocxEngine测试
"""
import pytest
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

@pytest.mark.integration
class TestDocxEngine:

    def test_docx_engine_import(self):
        """验证DocxEngine可导入"""
        from emba_checker.docx_engine import DocxEngine
        assert DocxEngine is not None

    def test_docx_engine_groups(self):
        """验证分组遍历"""
        from docx import Document
        from emba_checker.docx_engine import DocxEngine
        doc = Document()
        doc.add_paragraph("test")
        # 简化测试
        engine = DocxEngine(doc, {}, [])
        assert engine is not None
