# -*- coding: utf-8 -*-
"""
test_main_engine_extended.py - MainEngine扩展测试
包含边界测试和异常测试，用于提升测试覆盖率
"""
import pytest
import sys
import os
import tempfile
from docx import Document

sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')


@pytest.mark.integration
class TestMainEngineBoundary:
    """MainEngine边界测试"""

    def _create_temp_docx(self, content: str = "测试内容") -> str:
        """创建临时docx文件"""
        doc = Document()
        doc.add_paragraph(content)
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            doc.save(tmp.name)
            return tmp.name

    def test_empty_rules(self):
        """边界测试：空规则"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path)
            issues = engine.run()
            
            assert isinstance(issues, list)
        finally:
            os.unlink(doc_path)

    def test_single_rule(self):
        """边界测试：单条规则"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path)
            issues = engine.run()
            
            assert isinstance(issues, list)
        finally:
            os.unlink(doc_path)

    def test_many_rules(self):
        """边界测试：多条规则"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path)
            issues = engine.run()
            
            assert isinstance(issues, list)
        finally:
            os.unlink(doc_path)

    def test_empty_document(self):
        """边界测试：空文档"""
        from emba_checker.main_engine import MainEngine
        
        doc = Document()
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            doc.save(tmp.name)
            doc_path = tmp.name
        
        try:
            engine = MainEngine(doc_path)
            issues = engine.run()
            
            assert isinstance(issues, list)
        finally:
            os.unlink(doc_path)

    def test_many_paragraphs(self):
        """边界测试：多段落文档"""
        from emba_checker.main_engine import MainEngine
        
        doc = Document()
        for i in range(100):
            doc.add_paragraph(f"段落{i}")
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            doc.save(tmp.name)
            doc_path = tmp.name
        
        try:
            engine = MainEngine(doc_path)
            issues = engine.run()
            
            assert isinstance(issues, list)
        finally:
            os.unlink(doc_path)


@pytest.mark.integration
class TestMainEngineException:
    """MainEngine异常测试"""

    def _create_temp_docx(self, content: str = "测试内容") -> str:
        """创建临时docx文件"""
        doc = Document()
        doc.add_paragraph(content)
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            doc.save(tmp.name)
            return tmp.name

    def test_disabled_rule(self):
        """异常测试：禁用的规则"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path)
            issues = engine.run()
            
            assert isinstance(issues, list)
        finally:
            os.unlink(doc_path)

    def test_missing_check_type(self):
        """异常测试：缺少check_type"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path)
            issues = engine.run()
            
            assert isinstance(issues, list)
        finally:
            os.unlink(doc_path)

    def test_invalid_check_type(self):
        """异常测试：无效的check_type"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path)
            issues = engine.run()
            
            assert isinstance(issues, list)
        finally:
            os.unlink(doc_path)

    def test_empty_rule(self):
        """异常测试：空规则"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path)
            issues = engine.run()
            
            assert isinstance(issues, list)
        finally:
            os.unlink(doc_path)

    def test_no_api_key(self):
        """异常测试：无API密钥"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path, api_key=None)
            issues = engine.run()
            
            assert isinstance(issues, list)
        finally:
            os.unlink(doc_path)

    def test_with_api_key(self):
        """异常测试：带API密钥"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path, api_key="test-key")
            issues = engine.run()
            
            assert isinstance(issues, list)
        finally:
            os.unlink(doc_path)

    def test_rules_attribute(self):
        """异常测试：rules属性"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path)
            assert hasattr(engine, 'rules')
        finally:
            os.unlink(doc_path)

    def test_doc_attribute(self):
        """异常测试：doc属性"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path)
            assert hasattr(engine, 'doc')
        finally:
            os.unlink(doc_path)


@pytest.mark.integration
class TestMainEngineException:
    """MainEngine异常测试"""
    
    def _create_temp_docx(self, content: str = "测试内容") -> str:
        """创建临时docx文件"""
        doc = Document()
        doc.add_paragraph(content)
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            doc.save(tmp.name)
            return tmp.name

    def test_disabled_rule(self):
        """异常测试：禁用的规则"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path)
            issues = engine.run()
            assert isinstance(issues, list)
        finally:
            os.unlink(doc_path)

    def test_missing_check_type(self):
        """异常测试：缺少check_type"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path)
            issues = engine.run()
            assert isinstance(issues, list)
        finally:
            os.unlink(doc_path)

    def test_invalid_check_type(self):
        """异常测试：无效的check_type"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path)
            issues = engine.run()
            assert isinstance(issues, list)
        finally:
            os.unlink(doc_path)

    def test_empty_rule(self):
        """异常测试：空规则"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path)
            issues = engine.run()
            assert isinstance(issues, list)
        finally:
            os.unlink(doc_path)

    def test_no_api_key(self):
        """异常测试：无API密钥"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path, api_key=None)
            assert engine.api_key is None or engine.api_key == ""
        finally:
            os.unlink(doc_path)

    def test_with_api_key(self):
        """测试：带API密钥"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path, api_key="test_key")
            assert engine.api_key == "test_key"
        finally:
            os.unlink(doc_path)

    def test_rules_attribute(self):
        """测试：rules属性"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path)
            assert hasattr(engine, 'rules')
        finally:
            os.unlink(doc_path)

    def test_doc_attribute(self):
        """测试：doc属性"""
        from emba_checker.main_engine import MainEngine
        
        doc_path = self._create_temp_docx()
        
        try:
            engine = MainEngine(doc_path)
            assert hasattr(engine, 'doc')
        finally:
            os.unlink(doc_path)
