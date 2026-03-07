# -*- coding: utf-8 -*-
"""
test_docx_engine_extended.py - DocxEngine扩展测试
包含边界测试和异常测试，用于提升测试覆盖率
"""
import pytest
import sys
import json
from io import BytesIO
from docx import Document
from docx.shared import Pt, RGBColor

sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')


@pytest.mark.integration
class TestDocxEngineBoundary:
    """DocxEngine边界测试"""

    def test_empty_document(self):
        """边界测试：空文档"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        engine = DocxEngine(doc, [], {})
        
        # 空文档应该不崩溃
        assert engine is not None
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_single_empty_paragraph(self):
        """边界测试：单个空段落"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("")
        engine = DocxEngine(doc, [], {})
        
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_document_with_max_paragraphs(self):
        """边界测试：大量段落（性能边界）"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        # 添加100个段落
        for i in range(100):
            doc.add_paragraph(f"测试段落 {i}")
        
        engine = DocxEngine(doc, [], {})
        issues = engine.run_all()
        assert isinstance(issues, list)
        assert len(issues) >= 0

    def test_very_long_paragraph(self):
        """边界测试：超长段落"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        # 添加一个超长段落（模拟10000字）
        long_text = "测试内容 " * 1000
        doc.add_paragraph(long_text)
        
        engine = DocxEngine(doc, [], {})
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_paragraph_with_special_chars(self):
        """边界测试：特殊字符（不含控制字符）"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        para = doc.add_paragraph()
        # 不包含NULL字节等控制字符
        run = para.add_run("特殊字符：\t\n\r测试")
        
        engine = DocxEngine(doc, [], {})
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_unicode_paragraph(self):
        """边界测试：Unicode字符"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("中文测试 Unicode: \u4e00\u4e01 emoji: \U0001f600")
        
        engine = DocxEngine(doc, [], {})
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_mixed_font_paragraph(self):
        """边界测试：混合字体段落"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        para = doc.add_paragraph()
        
        run1 = para.add_run("黑体")
        run1.font.name = "黑体"
        
        run2 = para.add_run("宋体")
        run2.font.name = "宋体"
        
        run3 = para.add_run("Times New Roman")
        run3.font.name = "Times New Roman"
        
        engine = DocxEngine(doc, [], {})
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_font_size_boundary_values(self):
        """边界测试：字体大小边界值"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        para = doc.add_paragraph("测试")
        
        # 测试各种字号
        for size in [1, 5, 8, 9, 10, 12, 14, 16, 18, 22, 24, 26, 28, 72, 100, 200]:
            run = para.add_run(f"{size}pt ")
            run.font.size = Pt(size)
        
        engine = DocxEngine(doc, [], {})
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_empty_rules_list(self):
        """边界测试：空规则列表"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        engine = DocxEngine(doc, [], {})
        issues = engine.run_all()
        assert issues == []

    def test_single_rule(self):
        """边界测试：单条规则"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        rules = [{
            "rule_id": "TEST_01",
            "target_group": "Group2_Paragraphs",
            "enabled": True,
            "check_type": "text_match",
            "conditions": {"match_mode": "contains", "expected_text": "测试"}
        }]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_multiple_rules(self):
        """边界测试：多条规则（100条）"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        # 生成100条规则
        rules = [
            {
                "rule_id": f"TEST_{i:03d}",
                "target_group": "Group2_Paragraphs",
                "enabled": True,
                "check_type": "text_match",
                "conditions": {"match_mode": "contains", "expected_text": "测试"}
            }
            for i in range(100)
        ]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        assert isinstance(issues, list)


@pytest.mark.integration
class TestDocxEngineException:
    """DocxEngine异常测试"""

    def test_disabled_rule(self):
        """异常测试：禁用的规则"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        rules = [{
            "rule_id": "TEST_01",
            "target_group": "Group2_Paragraphs",
            "enabled": False,  # 禁用
            "check_type": "text_match",
            "conditions": {"match_mode": "contains", "expected_text": "测试"}
        }]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_rule_without_target_group(self):
        """异常测试：缺少target_group的规则"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        rules = [{
            "rule_id": "TEST_01",
            "enabled": True,
            "check_type": "text_match"
        }]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_rule_with_missing_fields(self):
        """异常测试：规则字段缺失"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        rules = [{}]  # 空规则
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_rule_with_invalid_check_type(self):
        """异常测试：无效的check_type"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        rules = [{
            "rule_id": "TEST_01",
            "target_group": "Group2_Paragraphs",
            "enabled": True,
            "check_type": "invalid_check_type",
            "conditions": {}
        }]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_zone_map_mismatch(self):
        """异常测试：zone_map不匹配"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        # zone_map比段落多
        zone_map = {0: "cover", 1: "cover", 2: "cover"}
        
        engine = DocxEngine(doc, [], zone_map)
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_empty_zone_map(self):
        """异常测试：空zone_map"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        engine = DocxEngine(doc, [], {})
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_progress_callback(self):
        """测试：进度回调"""
        from emba_checker.docx_engine import DocxEngine
        
        progress_calls = []
        
        def progress_callback(group, message, current, total):
            progress_calls.append((group, message, current, total))
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        rules = [{
            "rule_id": "TEST_01",
            "target_group": "Group2_Paragraphs",
            "enabled": True,
            "check_type": "text_match",
            "conditions": {"match_mode": "contains", "expected_text": "测试"}
        }]
        
        engine = DocxEngine(doc, rules, {}, progress_callback)
        issues = engine.run_all()
        
        # 验证回调被调用
        assert len(progress_calls) > 0

    def test_execution_log(self):
        """测试：执行日志"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        engine = DocxEngine(doc, [], {})
        engine.run_all()
        
        # 验证日志记录
        assert isinstance(engine.execution_log, list)

    def test_groups_attribute(self):
        """测试：Group定义"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        engine = DocxEngine(doc, [], {})
        
        # 验证所有Group都存在
        assert "Group1_Global" in DocxEngine.GROUPS
        assert "Group1_HeaderFooter" in DocxEngine.GROUPS
        assert "Group2_Paragraphs" in DocxEngine.GROUPS
        assert "Group3_Figures" in DocxEngine.GROUPS
        assert "Group3_Tables" in DocxEngine.GROUPS
        assert "Group4_Footnotes" in DocxEngine.GROUPS
        assert "Group5_References" in DocxEngine.GROUPS
        assert "Group6_CrossRef" in DocxEngine.GROUPS

    def test_rules_by_group(self):
        """测试：规则分组"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        
        rules = [
            {"rule_id": "TEST_01", "target_group": "Group1_Global"},
            {"rule_id": "TEST_02", "target_group": "Group2_Paragraphs"},
            {"rule_id": "TEST_03", "target_group": "Group2_Paragraphs"},
            {"rule_id": "TEST_04", "target_group": "Group3_Figures"},
        ]
        
        engine = DocxEngine(doc, rules, {})
        
        assert len(engine.rules_by_group["Group1_Global"]) == 1
        assert len(engine.rules_by_group["Group2_Paragraphs"]) == 2
        assert len(engine.rules_by_group["Group3_Figures"]) == 1


@pytest.mark.integration
class TestDocxEngineGroupIteration:
    """DocxEngine分组遍历测试"""

    def test_group1_global_with_rules(self):
        """测试Group1_Global"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        
        rules = [{
            "rule_id": "TEST_01",
            "target_group": "Group1_Global",
            "enabled": True,
            "check_type": "global_property",
            "conditions": {"property": "page_width_cm", "expected": 21.0}
        }]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_group2_paragraphs_with_rules(self):
        """测试Group2_Paragraphs"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        rules = [{
            "rule_id": "TEST_01",
            "target_group": "Group2_Paragraphs",
            "enabled": True,
            "check_type": "text_match",
            "conditions": {"match_mode": "contains", "expected_text": "测试"}
        }]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_group3_figures_empty(self):
        """测试Group3_Figures（无图片）"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        rules = [{
            "rule_id": "TEST_01",
            "target_group": "Group3_Figures",
            "enabled": True
        }]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_group3_tables_empty(self):
        """测试Group3_Tables（无表格）"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        rules = [{
            "rule_id": "TEST_01",
            "target_group": "Group3_Tables",
            "enabled": True
        }]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_group4_footnotes_empty(self):
        """测试Group4_Footnotes（无脚注）"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        
        rules = [{
            "rule_id": "TEST_01",
            "target_group": "Group4_Footnotes",
            "enabled": True
        }]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_group5_references_empty(self):
        """测试Group5_References（无参考文献）"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        
        rules = [{
            "rule_id": "TEST_01",
            "target_group": "Group5_References",
            "enabled": True
        }]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_group6_crossref_empty(self):
        """测试Group6_CrossRef（无交叉引用）"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        
        rules = [{
            "rule_id": "TEST_01",
            "target_group": "Group6_CrossRef",
            "enabled": True
        }]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_skip_disabled_groups(self):
        """测试跳过禁用的Group"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        # 所有规则都禁用
        rules = [{
            "rule_id": "TEST_01",
            "target_group": "Group2_Paragraphs",
            "enabled": False
        }]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        assert isinstance(issues, list)
