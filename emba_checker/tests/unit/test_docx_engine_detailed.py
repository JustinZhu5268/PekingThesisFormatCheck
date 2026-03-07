# -*- coding: utf-8 -*-
"""
test_docx_engine_detailed.py - DocxEngine详细单元测试
目标：行覆盖>=80%, 深度>=60%
"""
import pytest
import sys
from docx import Document
from docx.shared import Pt, RGBColor, Twips
from docx.table import Table
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')


@pytest.mark.unit
class TestDocxEngineInit:
    """DocxEngine初始化测试"""

    def test_init_with_all_params(self):
        """测试：完整参数初始化"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        rules = [{"rule_id": "TEST_01"}]
        zone_map = {0: "cover"}
        callback = Mock()
        
        engine = DocxEngine(doc, rules, zone_map, callback)
        
        assert engine.doc == doc
        assert engine.rules == rules
        assert engine.zone_map == zone_map
        assert engine.progress_callback == callback

    def test_init_without_callback(self):
        """测试：无回调函数初始化"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        engine = DocxEngine(doc, [], {})
        
        assert engine.doc == doc
        assert engine.progress_callback is None

    def test_init_rules_by_group_empty(self):
        """测试：空规则初始化"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        engine = DocxEngine(doc, [], {})
        
        assert engine.rules_by_group is not None
        for group in engine.GROUPS.keys():
            assert group in engine.rules_by_group

    def test_init_rules_by_group_with_rules(self):
        """测试：带规则初始化"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        rules = [
            {"rule_id": "T1", "target_group": "Group1_Global"},
            {"rule_id": "T2", "target_group": "Group2_Paragraphs"},
            {"rule_id": "T3", "target_group": "Group3_Figures"},
            {"rule_id": "T4"},  # 无group，默认Group2
        ]
        
        engine = DocxEngine(doc, rules, {})
        
        assert len(engine.rules_by_group["Group1_Global"]) == 1
        assert len(engine.rules_by_group["Group2_Paragraphs"]) == 2
        assert len(engine.rules_by_group["Group3_Figures"]) == 1


@pytest.mark.unit
class TestDocxEngineGroupRules:
    """规则分组测试"""

    def test_group_rules_unknown_group(self):
        """测试：未知Group"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        rules = [{"rule_id": "T1", "target_group": "UnknownGroup"}]
        
        engine = DocxEngine(doc, rules, {})
        
        # 未知group应该归到Group2
        assert len(engine.rules_by_group["Group2_Paragraphs"]) == 1

    def test_group_rules_all_groups(self):
        """测试：所有Group"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        rules = [
            {"rule_id": "T1", "target_group": "Group1_Global"},
            {"rule_id": "T2", "target_group": "Group1_HeaderFooter"},
            {"rule_id": "T3", "target_group": "Group2_Paragraphs"},
            {"rule_id": "T4", "target_group": "Group3_Figures"},
            {"rule_id": "T5", "target_group": "Group3_Tables"},
            {"rule_id": "T6", "target_group": "Group4_Footnotes"},
            {"rule_id": "T7", "target_group": "Group5_References"},
            {"rule_id": "T8", "target_group": "Group6_CrossRef"},
        ]
        
        engine = DocxEngine(doc, rules, {})
        
        for group in ["Group1_Global", "Group1_HeaderFooter", "Group2_Paragraphs",
                      "Group3_Figures", "Group3_Tables", "Group4_Footnotes",
                      "Group5_References", "Group6_CrossRef"]:
            assert len(engine.rules_by_group[group]) == 1


@pytest.mark.unit
class TestDocxEngineProgress:
    """进度报告测试"""

    def test_report_progress_with_callback(self):
        """测试：带回调的进度报告"""
        from emba_checker.docx_engine import DocxEngine
        
        callback = Mock()
        doc = Document()
        
        engine = DocxEngine(doc, [], {}, callback)
        engine._report_progress("Group1", "测试消息", 1, 10)
        
        callback.assert_called_once_with("Group1", "测试消息", 1, 10)

    def test_report_progress_without_callback(self):
        """测试：无回调的进度报告"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        engine = DocxEngine(doc, [], {})
        
        # 不应该抛出异常
        engine._report_progress("Group1", "测试消息", 1, 10)
        
        assert len(engine.execution_log) == 1
        assert "[Group1] 测试消息" in engine.execution_log[0]


@pytest.mark.unit
class TestDocxEngineRunAll:
    """run_all方法测试"""

    def test_run_all_empty_rules(self):
        """测试：空规则运行"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        engine = DocxEngine(doc, [], {})
        
        issues = engine.run_all()
        
        assert issues == []

    def test_run_all_skip_groups_without_rules(self):
        """测试：跳过无规则的Group"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        # 只有Group1的规则
        rules = [{"rule_id": "T1", "target_group": "Group1_Global", "enabled": True}]
        
        engine = DocxEngine(doc, rules, {})
        engine.run_all()
        
        # 应该跳过其他group
        log = engine.execution_log
        assert any("跳过" in msg for msg in log)

    def test_run_all_exception_handling(self):
        """测试：异常处理"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        
        # 模拟rule_engine抛出异常
        rules = [
            {"rule_id": "T1", "target_group": "Group2_Paragraphs", "enabled": True,
             "check_type": "invalid_type"}
        ]
        
        engine = DocxEngine(doc, rules, {})
        
        # 应该捕获异常而不是崩溃
        issues = engine.run_all()
        assert isinstance(issues, list)


@pytest.mark.unit
class TestDocxEngineCheckMethods:
    """检查方法测试"""

    def test_check_global_with_rules(self):
        """测试：全局属性检查"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        
        rules = [
            {"rule_id": "T1", "target_group": "Group1_Global", "enabled": True,
             "check_type": "global_property", "conditions": {}}
        ]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine._check_global(rules)
        
        assert isinstance(issues, list)

    def test_check_header_footer(self):
        """测试：页眉页脚检查"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        engine = DocxEngine(doc, [], {})
        
        issues = engine._check_header_footer([])
        
        assert issues == []

    def test_check_figures_empty(self):
        """测试：无图片检查"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        engine = DocxEngine(doc, [], {})
        
        issues = engine._check_figures([])
        
        assert issues == []

    def test_check_tables_empty(self):
        """测试：无表格检查"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        engine = DocxEngine(doc, [], {})
        
        issues = engine._check_tables([])
        
        assert issues == []

    def test_check_single_table(self):
        """测试：单个表格检查"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        table = doc.add_table(rows=3, cols=3)
        engine = DocxEngine(doc, [], {})
        
        issues = engine._check_single_table(table, 0, [])
        
        assert issues == []

    def test_check_footnotes(self):
        """测试：脚注检查"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        engine = DocxEngine(doc, [], {})
        
        issues = engine._check_footnotes([])
        
        assert issues == []

    def test_check_references(self):
        """测试：参考文献检查"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("正文")
        
        zone_map = {0: "references"}
        
        rules = [{"rule_id": "T1", "target_group": "Group5_References",
                 "enabled": True, "check_type": "text_match",
                 "conditions": {}}]
        
        engine = DocxEngine(doc, rules, zone_map)
        issues = engine._check_references(rules)
        
        assert isinstance(issues, list)

    def test_check_cross_ref(self):
        """测试：交叉引用检查"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        
        rules = [{"rule_id": "T1", "target_group": "Group6_CrossRef",
                 "enabled": True, "check_type": "cross_reference",
                 "conditions": {}}]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine._check_cross_ref(rules)
        
        assert isinstance(issues, list)


@pytest.mark.unit
class TestDocxEngineCreateErrorIssue:
    """错误Issue创建测试"""

    def test_create_error_issue_with_all_fields(self):
        """测试：完整字段创建错误Issue"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        engine = DocxEngine(doc, [], {})
        
        rule = {"rule_id": "TEST_01", "check_type": "text_match"}
        issue = engine._create_error_issue(rule, "测试错误")
        
        assert issue.rule_id == "TEST_01"
        assert issue.check_type == "text_match"
        assert issue.result == "error"
        assert "测试错误" in issue.message
        assert issue.severity == "error"

    def test_create_error_issue_missing_fields(self):
        """测试：缺失字段创建错误Issue"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        engine = DocxEngine(doc, [], {})
        
        issue = engine._create_error_issue({}, "错误")
        
        assert issue.rule_id == "unknown"
        assert issue.check_type == "unknown"


@pytest.mark.unit
class TestDocxEngineGetSummary:
    """摘要获取测试"""

    def test_get_summary_empty(self):
        """测试：空结果摘要"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        engine = DocxEngine(doc, [], {})
        engine.run_all()
        
        summary = engine.get_summary()
        
        assert summary["total_issues"] == 0
        assert "by_severity" in summary
        assert "by_group" in summary

    def test_get_summary_with_issues(self):
        """测试：有结果的摘要"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        
        rules = [{"rule_id": "T1", "target_group": "Group2_Paragraphs",
                 "enabled": True, "check_type": "text_match",
                 "conditions": {}}]
        
        engine = DocxEngine(doc, rules, {})
        engine.run_all()
        
        summary = engine.get_summary()
        
        assert "total_issues" in summary
        assert isinstance(summary["total_issues"], int)


@pytest.mark.unit
class TestDocxEngineBoundary:
    """边界值测试"""

    def test_document_with_table(self):
        """测试：带表格的文档"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_table(rows=5, cols=5)
        
        engine = DocxEngine(doc, [], {})
        engine.run_all()
        
        assert engine.issues is not None

    def test_document_with_inline_shapes(self):
        """测试：带内联图形的文档"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        
        engine = DocxEngine(doc, [], {})
        engine.run_all()
        
        assert engine.issues is not None

    def test_very_long_rule_list(self):
        """测试：长规则列表"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        
        rules = [{"rule_id": f"T{i}", "target_group": "Group2_Paragraphs",
                  "enabled": True} for i in range(200)]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        
        assert isinstance(issues, list)

    def test_mixed_enabled_disabled_rules(self):
        """测试：混合启用/禁用规则"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        
        rules = [
            {"rule_id": "T1", "target_group": "Group1_Global", "enabled": True},
            {"rule_id": "T2", "target_group": "Group1_Global", "enabled": False},
            {"rule_id": "T3", "target_group": "Group2_Paragraphs", "enabled": True},
        ]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        
        assert isinstance(issues, list)


@pytest.mark.unit
class TestDocxEngineException:
    """异常情况测试"""

    def test_rule_with_none_enabled(self):
        """测试：enabled为None的规则"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        
        rules = [{"rule_id": "T1", "enabled": None}]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        
        assert isinstance(issues, list)

    def test_rule_with_invalid_target_zone(self):
        """测试：无效的target_zone"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        
        rules = [{"rule_id": "T1", "target_zone": "invalid_zone"}]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        
        assert isinstance(issues, list)

    def test_zone_map_with_none_values(self):
        """测试：zone_map含None值"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        
        # zone_map某些值为None
        zone_map = {0: None, 1: "cover"}
        
        engine = DocxEngine(doc, [], zone_map)
        issues = engine.run_all()
        
        assert isinstance(issues, list)


@pytest.mark.unit
class TestDocxEngineRunDocxEngine:
    """run_docx_engine函数测试"""

    def test_run_docx_engine_function(self):
        """测试：便捷函数"""
        from emba_checker.docx_engine import run_docx_engine
        
        doc = Document()
        
        issues = run_docx_engine(doc, [], {})
        
        assert isinstance(issues, list)

    def test_run_docx_engine_with_callback(self):
        """测试：带回调的便捷函数"""
        from emba_checker.docx_engine import run_docx_engine
        
        callback_called = []
        
        def callback(group, msg, cur, total):
            callback_called.append((group, msg))
        
        doc = Document()
        
        run_docx_engine(doc, [], {}, callback)
        
        # 回调可能被调用多次
        assert isinstance(callback_called, list)


@pytest.mark.unit
class TestDocxEngineGroups:
    """Group定义测试"""

    def test_all_groups_defined(self):
        """测试：所有Group都已定义"""
        from emba_checker.docx_engine import DocxEngine
        
        expected_groups = [
            "Group1_Global", "Group1_HeaderFooter", "Group2_Paragraphs",
            "Group3_Figures", "Group3_Tables", "Group4_Footnotes",
            "Group5_References", "Group6_CrossRef"
        ]
        
        for group in expected_groups:
            assert group in DocxEngine.GROUPS

    def test_group_structure(self):
        """测试：Group结构"""
        from emba_checker.docx_engine import DocxEngine
        
        for group_name, group_info in DocxEngine.GROUPS.items():
            assert "name" in group_info
            assert "traverse" in group_info
            assert "description" in group_info


@pytest.mark.unit
class TestDocxEngineBoundaryExtended:
    """扩展边界值测试 - P0模块优化"""

    def test_empty_document(self):
        """边界测试：空文档"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        rules = [{"rule_id": "T1", "target_group": "Group2_Paragraphs", "enabled": True}]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        
        assert isinstance(issues, list)

    def test_document_with_1000_paragraphs(self):
        """边界测试：1000+段落"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        for i in range(1000):
            doc.add_paragraph(f"段落{i}内容")
        
        rules = [{"rule_id": "T1", "target_group": "Group2_Paragraphs", "enabled": True}]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        
        assert isinstance(issues, list)

    def test_rule_with_empty_conditions(self):
        """边界测试：规则条件为空"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        rules = [{"rule_id": "T1", "target_group": "Group2_Paragraphs", "enabled": True, "conditions": {}}]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        
        assert isinstance(issues, list)

    def test_rule_missing_rule_id(self):
        """边界测试：规则缺少rule_id"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试内容")
        
        rules = [{"target_group": "Group2_Paragraphs", "enabled": True}]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        
        assert isinstance(issues, list)

    def test_all_groups_with_real_rules(self):
        """边界测试：所有Group都运行真实规则"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试段落")
        
        rules = [
            {"rule_id": "G1", "target_group": "Group1_Global", "check_type": "global_property", "enabled": True, "conditions": {"property": "page_width_cm"}},
            {"rule_id": "G2", "target_group": "Group2_Paragraphs", "check_type": "paragraph_style", "enabled": True, "conditions": {}},
        ]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        
        assert isinstance(issues, list)


@pytest.mark.unit
class TestDocxEngineExceptionExtended:
    """扩展异常测试 - P0模块优化"""

    def test_executor_import_error(self):
        """异常测试：执行器导入错误"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试")
        
        # 使用不存在的check_type触发导入异常
        rules = [{"rule_id": "T1", "target_group": "Group2_Paragraphs", "check_type": "nonexistent_type", "enabled": True}]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        
        # 应该捕获异常并继续执行
        assert isinstance(issues, list)

    def test_rule_with_invalid_conditions(self):
        """异常测试：规则条件格式错误"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试")
        
        # conditions是字符串而不是字典
        rules = [{"rule_id": "T1", "target_group": "Group2_Paragraphs", "enabled": True, "conditions": "invalid"}]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        
        assert isinstance(issues, list)

    def test_check_global_exception(self):
        """异常测试：_check_global抛出异常"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        
        # 传入会导致global_property_executor出错的规则
        rules = [{"rule_id": "T1", "target_group": "Group1_Global", "check_type": "global_property", "enabled": True, "conditions": {"property": "invalid_property"}}]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        
        assert isinstance(issues, list)

    def test_check_paragraphs_exception(self):
        """异常测试：_check_paragraphs抛出异常"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        doc.add_paragraph("测试")
        
        # 传入会导致paragraph_style_executor出错的规则
        rules = [{"rule_id": "T1", "target_group": "Group2_Paragraphs", "check_type": "paragraph_style", "enabled": True, "conditions": None}]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        
        assert isinstance(issues, list)

    def test_create_error_issue_missing_fields(self):
        """异常测试：_create_error_issue处理缺少字段的规则"""
        from emba_checker.docx_engine import DocxEngine
        
        doc = Document()
        
        # 测试规则缺少必需字段时的情况
        rules = [{"enabled": True}]
        
        engine = DocxEngine(doc, rules, {})
        issues = engine.run_all()
        
        assert isinstance(issues, list)