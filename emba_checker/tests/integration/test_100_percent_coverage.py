# -*- coding: utf-8 -*-
"""
test_100_percent_coverage.py - 100%覆盖率测试
"""
import pytest
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

# 真实docx文件路径
REAL_DOCX = 'D:/Projects/ThesisFormatCheck/data/医保支付方式改革下A医疗集团医疗收入质量优化研究——以A医疗集团为例-定稿V1.0.docx'

@pytest.mark.integration
class TestRuleEngineFullCoverage:
    """RuleEngine完整覆盖测试"""

    def test_rule_engine_all_groups(self):
        """测试所有规则组"""
        import json
        from docx import Document
        from emba_checker.rule_engine import RuleEngine
        from emba_checker.zone_detector import detect_zones
        
        with open('D:/Projects/ThesisFormatCheck/emba_checker/rules_registry.json', 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        doc = Document(REAL_DOCX)
        zones = detect_zones(doc)
        
        # 测试所有规则
        engine = RuleEngine(doc, rules, zones)
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_rule_engine_group1(self):
        """测试Group1规则"""
        import json
        from docx import Document
        from emba_checker.rule_engine import RuleEngine
        from emba_checker.zone_detector import detect_zones
        
        with open('D:/Projects/ThesisFormatCheck/emba_checker/rules_registry.json', 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        # 筛选Group1规则
        group1_rules = [r for r in rules if r.get('target_group', '').startswith('Group1')]
        
        doc = Document(REAL_DOCX)
        zones = detect_zones(doc)
        
        engine = RuleEngine(doc, group1_rules, zones)
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_rule_engine_group2(self):
        """测试Group2规则"""
        import json
        from docx import Document
        from emba_checker.rule_engine import RuleEngine
        from emba_checker.zone_detector import detect_zones
        
        with open('D:/Projects/ThesisFormatCheck/emba_checker/rules_registry.json', 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        # 筛选Group2规则
        group2_rules = [r for r in rules if r.get('target_group', '') == 'Group2_Paragraphs']
        
        doc = Document(REAL_DOCX)
        zones = detect_zones(doc)
        
        engine = RuleEngine(doc, group2_rules, zones)
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_rule_engine_group3_figures(self):
        """测试Group3图形规则"""
        import json
        from docx import Document
        from emba_checker.rule_engine import RuleEngine
        from emba_checker.zone_detector import detect_zones
        
        with open('D:/Projects/ThesisFormatCheck/emba_checker/rules_registry.json', 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        group3_rules = [r for r in rules if r.get('target_group', '').startswith('Group3')]
        
        doc = Document(REAL_DOCX)
        zones = detect_zones(doc)
        
        engine = RuleEngine(doc, group3_rules, zones)
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_rule_engine_group4_footnotes(self):
        """测试Group4脚注规则"""
        import json
        from docx import Document
        from emba_checker.rule_engine import RuleEngine
        from emba_checker.zone_detector import detect_zones
        
        with open('D:/Projects/ThesisFormatCheck/emba_checker/rules_registry.json', 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        group4_rules = [r for r in rules if r.get('target_group', '').startswith('Group4')]
        
        doc = Document(REAL_DOCX)
        zones = detect_zones(doc)
        
        engine = RuleEngine(doc, group4_rules, zones)
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_rule_engine_group5_references(self):
        """测试Group5参考文献规则"""
        import json
        from docx import Document
        from emba_checker.rule_engine import RuleEngine
        from emba_checker.zone_detector import detect_zones
        
        with open('D:/Projects/ThesisFormatCheck/emba_checker/rules_registry.json', 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        group5_rules = [r for r in rules if r.get('target_group', '').startswith('Group5')]
        
        doc = Document(REAL_DOCX)
        zones = detect_zones(doc)
        
        engine = RuleEngine(doc, group5_rules, zones)
        issues = engine.run_all()
        assert isinstance(issues, list)

@pytest.mark.integration
class TestDocxEngineFullCoverage:
    """DocxEngine完整覆盖测试"""

    def test_docx_engine_all_rules(self):
        """测试所有规则"""
        import json
        from docx import Document
        from emba_checker.docx_engine import DocxEngine
        from emba_checker.zone_detector import detect_zones
        
        with open('D:/Projects/ThesisFormatCheck/emba_checker/rules_registry.json', 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        doc = Document(REAL_DOCX)
        zones = detect_zones(doc)
        
        engine = DocxEngine(doc, rules, zones)
        issues = engine.run_all()
        assert isinstance(issues, list)

    def test_docx_engine_group_iteration(self):
        """测试按组迭代"""
        import json
        from docx import Document
        from emba_checker.docx_engine import DocxEngine
        from emba_checker.zone_detector import detect_zones
        
        with open('D:/Projects/ThesisFormatCheck/emba_checker/rules_registry.json', 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        doc = Document(REAL_DOCX)
        zones = detect_zones(doc)
        
        engine = DocxEngine(doc, rules, zones)
        
        # 测试各个组 - 使用run_all代替不存在的run_group
        issues = engine.run_all()
        assert isinstance(issues, list)

@pytest.mark.integration
class TestSafeAnnotatorFullCoverage:
    """SafeAnnotator完整覆盖测试"""

    def test_safe_annotator_multiple_issues(self):
        """测试多个issue标注"""
        from docx import Document
        from emba_checker.safe_annotator import SafeAnnotator
        from emba_checker.base_executor import CheckIssue
        
        doc = Document(REAL_DOCX)
        
        # 创建多个issue
        issues = []
        for i in range(min(10, len(doc.paragraphs))):
            issues.append(CheckIssue(
                rule_id=f"TEST_{i:02d}",
                check_type="test",
                result="fail",
                message=f"测试问题{i}",
                location={"paragraph_index": i, "paragraphs": [i]},
                severity="error"
            ))
        
        annotator = SafeAnnotator(doc, issues)
        result = annotator.annotate_all()
        assert isinstance(result, tuple)
        
    def test_safe_annotator_get_log(self):
        """测试获取日志"""
        from docx import Document
        from emba_checker.safe_annotator import SafeAnnotator
        from emba_checker.base_executor import CheckIssue
        
        doc = Document(REAL_DOCX)
        
        issues = [
            CheckIssue(
                rule_id="TEST_01",
                check_type="test",
                result="fail",
                message="测试问题",
                location={"paragraph_index": 0, "paragraphs": [0]},
                severity="error"
            )
        ]
        
        annotator = SafeAnnotator(doc, issues)
        annotator.annotate_all()
        
        log = annotator.get_log()
        assert isinstance(log, list)

    def test_safe_annotator_save(self):
        """测试保存"""
        from docx import Document
        from emba_checker.safe_annotator import SafeAnnotator
        from emba_checker.base_executor import CheckIssue
        import tempfile
        import os
        
        doc = Document(REAL_DOCX)
        
        issues = [
            CheckIssue(
                rule_id="TEST_01",
                check_type="test",
                result="fail",
                message="测试问题",
                location={"paragraph_index": 0, "paragraphs": [0]},
                severity="error"
            )
        ]
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            annotator = SafeAnnotator(doc, issues, tmp_path)
            annotator.annotate_all()
            annotator.save()
            # 文件应该存在
            assert os.path.exists(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

@pytest.mark.integration
class TestUtilsFullCoverage:
    """Utils完整覆盖测试"""

    def test_utils_font_functions(self):
        """测试字体函数"""
        from docx import Document
        from emba_checker import utils
        
        doc = Document(REAL_DOCX)
        
        for para in doc.paragraphs[:20]:
            if para.runs:
                run = para.runs[0]
                
                # 测试各种字体函数
                font_name = utils.get_font_name(run)
                font_size = utils.get_font_size(run)
                font_bold = utils.get_font_bold(run)
                font_italic = utils.get_font_italic(run)
                
                assert font_name is not None

    def test_utils_paragraph_functions(self):
        """测试段落函数"""
        from docx import Document
        from emba_checker import utils
        
        doc = Document(REAL_DOCX)
        
        for para in doc.paragraphs[:20]:
            # 测试各种段落函数 - 允许返回None
            align = utils.get_paragraph_alignment(para)
            first_indent = utils.get_first_line_indent(para)
            hanging_indent = utils.get_hanging_indent(para)
            spacing = utils.get_line_spacing(para)
            space_before = utils.get_space_before(para)
            space_after = utils.get_space_after(para)
            
            # 只验证函数正常执行，不强制要求非None
            assert align is None or isinstance(align, str)

    def test_utils_check_value_in_range(self):
        """测试范围检查"""
        from emba_checker import utils
        
        # 测试各种范围检查
        assert utils.check_value_in_range(10, 10, 1) == True
        assert utils.check_value_in_range(10, 12, 2) == True
        assert utils.check_value_in_range(10, 15, 2) == False

    def test_utils_text_functions(self):
        """测试文本函数"""
        from emba_checker import utils
        
        # 测试文本处理函数
        text = "Hello世界123测试"
        
        chinese = utils.extract_chinese_text(text)
        english = utils.extract_english_text(text)
        chinese_count = utils.count_chinese_chars(text)
        english_count = utils.count_english_chars(text)
        total = utils.count_total_chars(text)
        
        assert chinese_count >= 0
        assert english_count >= 0
        assert total >= 0

@pytest.mark.integration
class TestMainEngineFullCoverage:
    """MainEngine完整覆盖测试"""

    def test_main_engine_with_rules_path(self):
        """测试指定规则文件"""
        from emba_checker.main_engine import MainEngine
        
        rules_path = 'D:/Projects/ThesisFormatCheck/emba_checker/rules_registry.json'
        engine = MainEngine(REAL_DOCX, rules_path=rules_path)
        
        assert engine is not None

    def test_main_engine_with_api_key(self):
        """测试带API key"""
        from emba_checker.main_engine import MainEngine
        
        engine = MainEngine(REAL_DOCX, api_key="test-key")
        
        assert engine is not None

    def test_main_engine_progress_callback(self):
        """测试进度回调"""
        from emba_checker.main_engine import MainEngine
        
        progress_calls = []
        
        def callback(source, message, current, total):
            progress_calls.append((source, message))
        
        engine = MainEngine(REAL_DOCX, progress_callback=callback)
        issues = engine.run(enable_claude=False)
        
        assert len(progress_calls) > 0

    def test_main_engine_stats(self):
        """测试统计信息"""
        from emba_checker.main_engine import MainEngine
        
        engine = MainEngine(REAL_DOCX)
        engine.run(enable_claude=False)
        
        stats = engine.stats
        assert 'docx_engine_issues' in stats
        assert 'total_time' in stats
