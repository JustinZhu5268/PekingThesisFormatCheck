# -*- coding: utf-8 -*-
"""
conftest.py - 全局 Fixture 规范
"""
import pytest
import json
import os
from docx import Document
from docx.shared import Pt, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH


def pytest_configure(config):
    """注册自定义 markers"""
    config.addinivalue_line("markers", "unit: L1 单元测试（快速，无IO）")
    config.addinivalue_line("markers", "integration: L2 集成测试（读写docx文件）")
    config.addinivalue_line("markers", "e2e: L3 端到端测试（完整流程）")
    config.addinivalue_line("markers", "slow: 耗时较长的测试（Claude API等）")
    config.addinivalue_line("markers", "prd: PRD需求标记测试")

# Docx 工厂类
class DocxFactory:
    @staticmethod
    def create_minimal():
        """最小化文档：只有一个段落"""
        doc = Document()
        doc.add_paragraph("测试文档")
        return doc

    @staticmethod
    def create_with_zones():
        """包含所有标准区域的文档"""
        doc = Document()
        
        # 封面
        p = doc.add_paragraph("论文标题测试")
        
        # 版权声明
        doc.add_paragraph("版权声明")
        doc.add_paragraph("本人同意...")
        
        # 原创性声明
        doc.add_paragraph("原创性声明")
        
        # 摘要
        doc.add_heading("摘  要", level=1)
        doc.add_paragraph("本研究以某公司为例，探讨了战略管理问题...")
        
        # 关键词
        doc.add_paragraph("关键词：战略管理；案例研究；企业转型")
        
        # 英文摘要
        doc.add_heading("ABSTRACT", level=1)
        doc.add_paragraph("This study explores strategic management...")
        doc.add_paragraph("Keywords: strategic management; case study")
        
        # 目录
        doc.add_heading("目  录", level=1)
        
        # 正文
        doc.add_heading("第一章 绪论", level=1)
        doc.add_paragraph("本研究旨在探讨...")
        
        doc.add_heading("1.1 研究背景", level=2)
        doc.add_paragraph("随着经济发展...")
        
        doc.add_heading("第二章 文献综述", level=1)
        doc.add_paragraph("国内外学者对此问题...")
        
        # 参考文献
        doc.add_heading("参考文献", level=1)
        doc.add_paragraph("[1] 张三. 管理学研究[M]. 北京: 北京大学出版社, 2020.")
        
        # 附录
        doc.add_heading("附录", level=1)
        doc.add_paragraph("附录A：调查问卷")
        
        # 致谢
        doc.add_heading("致  谢", level=1)
        doc.add_paragraph("感谢我的导师...")
        
        return doc

    @staticmethod
    def create_paragraph_with_font(text, font_name="宋体", font_size_pt=12,
                                    bold=False, alignment=None):
        """创建单段落文档，精确控制字体属性"""
        doc = Document()
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.name = font_name
        run.font.size = Pt(font_size_pt)
        run.font.bold = bold
        if alignment is not None:
            p.paragraph_format.alignment = alignment
        return doc, p

    @staticmethod
    def create_with_page_settings(width_cm=21.0, height_cm=29.7,
                                   top_cm=2.54, bottom_cm=2.54,
                                   left_cm=3.17, right_cm=3.17):
        """创建指定页面设置的文档"""
        doc = Document()
        section = doc.sections[0]
        section.page_width = Cm(width_cm)
        section.page_height = Cm(height_cm)
        section.top_margin = Cm(top_cm)
        section.bottom_margin = Cm(bottom_cm)
        section.left_margin = Cm(left_cm)
        section.right_margin = Cm(right_cm)
        return doc

    @staticmethod
    def create_with_errors():
        """故意包含多种格式错误的文档"""
        doc = DocxFactory.create_with_zones()
        
        # 错误1：封面标题用宋体而非黑体
        if doc.paragraphs[0].runs:
            doc.paragraphs[0].runs[0].font.name = "宋体"
        
        # 错误2：正文中使用英文逗号
        doc.add_paragraph("本研究发现,结果显著。")  # 英文逗号
        
        # 错误3：使用第一人称
        doc.add_paragraph("我认为这个结论是合理的。")
        
        # 错误4：口语化表达
        doc.add_paragraph("众所周知，管理学是一门重要的学科。")
        
        return doc

@pytest.fixture
def docx_factory():
    """docx 文档工厂"""
    return DocxFactory()

@pytest.fixture
def minimal_doc():
    """最小化文档"""
    return DocxFactory.create_minimal()

@pytest.fixture
def zoned_doc():
    """包含所有区域的标准文档"""
    return DocxFactory.create_with_zones()

@pytest.fixture
def error_doc():
    """包含故意错误的文档"""
    return DocxFactory.create_with_errors()

@pytest.fixture
def sample_rules():
    """小规模测试用规则列表（10条代表性规则）"""
    return [
        {
            "rule_id": "PAGE_01",
            "check_type": "global_property",
            "target_group": "Group1_Global",
            "target_zone": ["*"],
            "engine": "Python",
            "urgency": "★★★★★",
            "conditions": {"property": "page_width_cm", "expected": 21.0, "tolerance": 0.05, "compare": "equals"},
            "error_message": "纸张宽度必须为A4（21cm）",
            "enabled": True,
        },
        {
            "rule_id": "BODY_01",
            "check_type": "paragraph_style",
            "target_group": "Group2_Paragraphs",
            "target_zone": ["body_chapter"],
            "engine": "Python",
            "urgency": "★★★★★",
            "conditions": {"font_name_cn": "宋体", "font_size_pt": 12, "alignment": "JUSTIFY"},
            "error_message": "正文必须宋体小四号两端对齐",
            "enabled": True,
        },
        {
            "rule_id": "PUNCT_01",
            "check_type": "regex_match",
            "target_group": "Group2_Paragraphs",
            "target_zone": ["body_chapter", "abstract_cn"],
            "engine": "Python",
            "urgency": "★★★★★",
            "conditions": {"pattern": ",", "match_mode": "must_not_match"},
            "error_message": "中文正文中不应使用英文逗号",
            "enabled": True,
        },
        {
            "rule_id": "BODY_02",
            "check_type": "count_check",
            "target_group": "Group2_Paragraphs",
            "target_zone": ["body_chapter"],
            "engine": "Python",
            "urgency": "★★★★★",
            "conditions": {"count_type": "chinese_chars", "min_value": 20000},
            "error_message": "正文字数不少于2万字",
            "enabled": True,
        },
        {
            "rule_id": "TEXT_01",
            "check_type": "forbidden_words",
            "target_group": "Group2_Paragraphs",
            "target_zone": ["body_chapter"],
            "engine": "Python",
            "urgency": "★★★★☆",
            "conditions": {"inline_words": ["我认为","我觉得","众所周知"], "match_mode": "any"},
            "error_message": "正文中禁止使用口语化/第一人称表达",
            "enabled": True,
        },
    ]

@pytest.fixture
def tmp_docx(tmp_path):
    """提供一个临时 docx 路径用于写入测试"""
    return str(tmp_path / "test_output.docx")

@pytest.fixture
def tmp_txt(tmp_path):
    """提供一个临时 txt 路径用于报告输出"""
    return str(tmp_path / "test_report.txt")

@pytest.fixture
def mock_claude_response(mocker):
    """Mock Claude API，返回预设的结构化响应"""
    mock_client = mocker.patch("anthropic.Anthropic")
    mock_response = mocker.MagicMock()
    mock_response.content = [mocker.MagicMock(text=json.dumps({
        "has_purpose": True, "has_method": True,
        "has_result": False, "has_conclusion": True,
        "missing_elements": ["研究结果"],
        "suggestion": "摘要缺少具体研究结果描述"
    }))]
    mock_client.return_value.messages.create.return_value = mock_response
    return mock_client
