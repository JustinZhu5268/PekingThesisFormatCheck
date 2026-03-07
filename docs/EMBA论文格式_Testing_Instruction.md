# EMBA 论文审查工具 — 测试体系建设指令

> **目标读者**: Cursor AI 编程助手
> **前置依赖**: 已按 PRD 完成 Step 0 ~ Step 9 的开发
> **配套文件**: `EMBA论文审查工具_PRD终极版.md`

---

# 一、总体要求

请阅读项目的 PRD（`EMBA论文审查工具_PRD终极版.md`），然后为整个项目建立**三层测试体系**：

| 测试层级 | 方法论 | 目标 | 工具 |
|---------|--------|------|------|
| **L1 单元测试** | 每个模块独立测试，mock 所有外部依赖 | 每个函数的输入输出正确性 | pytest + pytest-mock |
| **L2 集成测试** | 多模块联动，使用真实 docx fixture | 模块间数据流正确性 | pytest + python-docx fixtures |
| **L3 E2E 测试** | 从 GUI 操作到最终输出文件 | 用户视角的端到端正确性 | pytest + threading（模拟GUI事件） |

**技术选型**：
- 框架：`pytest >= 8.0`（不要用 unittest）
- Mock：`pytest-mock`（`mocker` fixture）
- 覆盖率：`pytest-cov`，目标 **≥ 85%** 行覆盖率
- 参数化：大量使用 `@pytest.mark.parametrize` 减少重复代码
- Fixture：用 `conftest.py` 统一管理 docx fixture 工厂
- 标记：`@pytest.mark.unit` / `@pytest.mark.integration` / `@pytest.mark.e2e` / `@pytest.mark.slow`

**在 `requirements.txt` 中追加**：
```
pytest>=8.0
pytest-mock>=3.12
pytest-cov>=4.1
```

---

# 二、测试目录结构

```
emba_checker/
├── tests/
│   ├── conftest.py                # 全局 fixture（docx工厂、规则库fixture、mock配置）
│   ├── pytest.ini                 # pytest 配置（标记注册、默认参数）
│   │
│   ├── unit/                      # L1 单元测试
│   │   ├── test_utils.py
│   │   ├── test_config.py
│   │   ├── test_md_parser.py
│   │   ├── test_verify_coverage.py
│   │   ├── test_zone_detector.py
│   │   ├── test_rule_executors.py  # 最重要，7种check_type × 多种输入
│   │   ├── test_docx_engine.py
│   │   ├── test_claude_engine.py
│   │   ├── test_safe_annotator.py
│   │   ├── test_issue_merger.py
│   │   └── test_orchestrator.py
│   │
│   ├── integration/               # L2 集成测试
│   │   ├── test_md_to_registry.py  # MD解析→规则库→覆盖率核对
│   │   ├── test_engine_pipeline.py # 规则库→zone→引擎→Issue
│   │   ├── test_annotator_docx.py  # Issue→标注→docx文件完整性
│   │   └── test_dual_engine.py     # Python引擎 + Claude引擎(mock) 合并
│   │
│   ├── e2e/                        # L3 端到端测试
│   │   ├── test_full_pipeline.py   # 输入docx→输出标注docx+报告txt
│   │   └── test_gui_flow.py        # GUI事件模拟（无头测试）
│   │
│   └── fixtures/                   # 测试用 docx 文件和数据
│       ├── docx_factory.py         # 程序化生成测试docx的工厂类
│       ├── sample_compliant.docx   # 合规模板
│       ├── sample_errors.docx      # 故意错误
│       ├── sample_empty.docx       # 空白文档
│       ├── sample_minimal_md.md    # 最小化MD清单（用于快速测试）
│       └── sample_rules.json       # 预生成的小规模规则库
```

---

# 三、pytest 配置

```ini
# tests/pytest.ini
[pytest]
testpaths = tests
markers =
    unit: L1 单元测试（快速，无IO）
    integration: L2 集成测试（读写docx文件）
    e2e: L3 端到端测试（完整流程）
    slow: 耗时较长的测试（Claude API等）
addopts = -v --tb=short --strict-markers
```

**运行命令**：
```bash
# 仅跑单元测试（开发时高频运行，< 10秒）
pytest -m unit

# 跑单元 + 集成（提交前运行，< 30秒）
pytest -m "unit or integration"

# 全量测试（发版前运行）
pytest

# 带覆盖率报告
pytest --cov=emba_checker --cov-report=html --cov-fail-under=85
```

---

# 四、conftest.py — 全局 Fixture 规范

```python
# tests/conftest.py
import pytest
import json
import os
from docx import Document
from docx.shared import Pt, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH


# ============================================================
#  Docx 工厂 — 程序化生成测试文档（核心 fixture）
# ============================================================

class DocxFactory:
    """
    程序化生成各种测试用 docx 文件。
    用法：factory.create_compliant() 返回一个符合所有格式要求的 Document 对象。
    """

    @staticmethod
    def create_minimal():
        """最小化文档：只有一个段落"""
        doc = Document()
        doc.add_paragraph("测试文档")
        return doc

    @staticmethod
    def create_with_zones():
        """包含所有标准区域的文档，用于 zone_detector 测试"""
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
        """创建单段落文档，精确控制字体属性，用于 paragraph_style 执行器测试"""
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
        """创建指定页面设置的文档，用于 global_property 执行器测试"""
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
        doc.paragraphs[0].runs[0].font.name = "宋体"
        # 错误2：正文中使用英文逗号
        doc.add_paragraph("本研究发现,结果显著。")  # 英文逗号
        # 错误3：使用第一人称
        doc.add_paragraph("我认为这个结论是合理的。")
        # 错误4：口语化表达
        doc.add_paragraph("众所周知，管理学是一门重要的学科。")
        return doc


# ============================================================
#  Pytest Fixtures
# ============================================================

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
def sample_zone_map():
    """与 zoned_doc 对应的预期 zone_map"""
    # 这个fixture需要根据 create_with_zones() 的段落数对应填写
    # Cursor 在实现时应根据实际段落索引调整
    return {
        0: "cover",
        1: "copyright", 2: "copyright",
        3: "declaration",
        4: "abstract_cn", 5: "abstract_cn", 6: "abstract_cn",
        7: "abstract_en", 8: "abstract_en", 9: "abstract_en",
        10: "toc",
        11: "body_chapter", 12: "body_chapter",
        13: "body_chapter", 14: "body_chapter",
        15: "body_chapter", 16: "body_chapter",
        17: "references", 18: "references",
        19: "appendix", 20: "appendix",
        21: "acknowledgment", 22: "acknowledgment",
    }


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


@pytest.fixture
def tmp_docx(tmp_path):
    """提供一个临时 docx 路径用于写入测试"""
    return str(tmp_path / "test_output.docx")


@pytest.fixture
def tmp_txt(tmp_path):
    """提供一个临时 txt 路径用于报告输出"""
    return str(tmp_path / "test_report.txt")
```

---

# 五、L1 单元测试详细规范

## 5.1 test_utils.py — 工具函数

```python
import pytest
from utils import emu_to_cm, cm_to_emu, emu_to_pt, pt_to_emu, get_east_asia_font


@pytest.mark.unit
class TestUnitConversion:
    """单位换算函数测试"""

    @pytest.mark.parametrize("emu, expected_cm", [
        (360000, 1.0),
        (7200000, 20.0),
        (0, 0.0),
        (180000, 0.5),
    ])
    def test_emu_to_cm(self, emu, expected_cm):
        assert abs(emu_to_cm(emu) - expected_cm) < 0.001

    @pytest.mark.parametrize("cm, expected_emu", [
        (1.0, 360000),
        (2.54, 914400),
    ])
    def test_cm_to_emu(self, cm, expected_emu):
        assert cm_to_emu(cm) == expected_emu

    @pytest.mark.parametrize("emu, expected_pt", [
        (12700, 1.0),
        (152400, 12.0),  # 小四号
        (330200, 26.0),  # 一号
    ])
    def test_emu_to_pt(self, emu, expected_pt):
        assert abs(emu_to_pt(emu) - expected_pt) < 0.01
```

## 5.2 test_md_parser.py — MD解析器

```python
@pytest.mark.unit
class TestMdParser:

    def test_parse_extracts_correct_count(self, tmp_path):
        """验证解析出的规则数与MD中✅+⚠️行数一致"""
        md = self._create_mini_md(tmp_path)
        rules = parse_md_to_rules(str(md))
        assert len(rules) == 3  # mini md有3条可编程规则

    def test_parse_excludes_manual_rules(self, tmp_path):
        """验证❌标记的规则被排除"""
        md = self._create_mini_md(tmp_path)
        rules = parse_md_to_rules(str(md))
        rule_ids = [r["rule_id"] for r in rules]
        assert not any("manual" in rid.lower() for rid in rule_ids)

    def test_parse_generates_composite_key(self, tmp_path):
        """验证同名要素在不同章节生成不同的复合Key"""
        md = self._create_md_with_duplicate_names(tmp_path)
        rules = parse_md_to_rules(str(md))
        keys = [r["md_source_key"] for r in rules]
        assert len(keys) == len(set(keys))  # 无重复

    def test_parse_infers_paragraph_style(self, tmp_path):
        """验证含字体/字号关键词的规则被推断为paragraph_style"""
        md = self._create_mini_md(tmp_path)
        rules = parse_md_to_rules(str(md))
        font_rule = [r for r in rules if "字体" in r["format_requirement"]]
        assert font_rule[0]["check_type"] == "paragraph_style"

    def test_parse_extracts_font_size(self, tmp_path):
        """验证字号从格式要求文本中正确提取"""
        md = self._create_mini_md(tmp_path)
        rules = parse_md_to_rules(str(md))
        cover_rule = [r for r in rules if "COVER" in r["rule_id"]][0]
        assert cover_rule["conditions"].get("font_size_pt") == 26  # 一号=26pt

    def test_parse_unknown_fallback(self, tmp_path):
        """无法推断的规则标记为unknown"""
        md = self._create_md_with_ambiguous_rule(tmp_path)
        rules = parse_md_to_rules(str(md))
        ambiguous = [r for r in rules if r["check_type"] == "unknown"]
        assert len(ambiguous) >= 1
        assert ambiguous[0]["conditions"].get("_needs_manual_review") is True

    @staticmethod
    def _create_mini_md(tmp_path):
        """创建最小化MD清单用于测试"""
        content = """# 测试清单\n\n## 一、封面页格式\n\n| 要素 | 格式要求 | 紧急程度 | 可编程性 | 检测方法说明 |\n|------|----------|----------|----------|--------------|\n| **论文题目** | 黑体，一号，加粗，居中 | ★★★★★ | ✅ | 字体检测 |\n| **日期** | 宋体，三号 | ★★★★★ | ✅ | 正则匹配 |\n| **题目学术性** | 有学术基础 | ★★★★☆ | ❌ | 需人工判断 |\n| **研究方向** | 8个汉字，指定列表 | ★★★★★ | ⚠️ | 词库匹配 |\n"""
        p = tmp_path / "test.md"
        p.write_text(content, encoding="utf-8")
        return p
```

## 5.3 test_zone_detector.py — 区域识别

```python
@pytest.mark.unit
class TestZoneDetector:

    def test_cover_detected(self, zoned_doc):
        zone_map = detect_zones(zoned_doc)
        assert zone_map[0] == "cover"

    def test_abstract_cn_detected(self, zoned_doc):
        zone_map = detect_zones(zoned_doc)
        abstract_zones = [i for i, z in zone_map.items() if z == "abstract_cn"]
        assert len(abstract_zones) >= 2  # 标题 + 正文 + 关键词

    def test_abstract_en_detected(self, zoned_doc):
        zone_map = detect_zones(zoned_doc)
        en_zones = [i for i, z in zone_map.items() if z == "abstract_en"]
        assert len(en_zones) >= 1

    def test_body_chapter_detected(self, zoned_doc):
        zone_map = detect_zones(zoned_doc)
        body_zones = [i for i, z in zone_map.items() if z == "body_chapter"]
        assert len(body_zones) >= 4  # 两章+节标题+段落

    def test_references_detected(self, zoned_doc):
        zone_map = detect_zones(zoned_doc)
        ref_zones = [i for i, z in zone_map.items() if z == "references"]
        assert len(ref_zones) >= 1

    def test_acknowledgment_detected(self, zoned_doc):
        zone_map = detect_zones(zoned_doc)
        ack_zones = [i for i, z in zone_map.items() if z == "acknowledgment"]
        assert len(ack_zones) >= 1

    def test_empty_doc_no_crash(self, minimal_doc):
        """空白文档不崩溃，全部归为cover"""
        zone_map = detect_zones(minimal_doc)
        assert all(z == "cover" for z in zone_map.values())

    def test_all_paragraphs_assigned(self, zoned_doc):
        """每个段落都必须有zone标签"""
        zone_map = detect_zones(zoned_doc)
        assert len(zone_map) == len(zoned_doc.paragraphs)
```

## 5.4 test_rule_executors.py — 七种执行器（最核心）

```python
@pytest.mark.unit
class TestParagraphStyleExecutor:
    """paragraph_style 执行器测试"""

    def test_correct_font_passes(self, docx_factory):
        doc, p = docx_factory.create_paragraph_with_font(
            "测试", font_name="宋体", font_size_pt=12)
        cond = {"font_name_cn": "宋体", "font_size_pt": 12}
        issues = paragraph_style_executor(p, cond)
        assert len(issues) == 0

    def test_wrong_font_fails(self, docx_factory):
        doc, p = docx_factory.create_paragraph_with_font(
            "测试", font_name="黑体", font_size_pt=12)
        cond = {"font_name_cn": "宋体", "font_size_pt": 12}
        issues = paragraph_style_executor(p, cond)
        assert len(issues) >= 1
        assert "宋体" in issues[0].message or "font" in issues[0].message.lower()

    def test_wrong_size_fails(self, docx_factory):
        doc, p = docx_factory.create_paragraph_with_font(
            "测试", font_name="宋体", font_size_pt=16)
        cond = {"font_name_cn": "宋体", "font_size_pt": 12}
        issues = paragraph_style_executor(p, cond)
        assert len(issues) >= 1

    def test_null_condition_skipped(self, docx_factory):
        """conditions中为null的项不检查"""
        doc, p = docx_factory.create_paragraph_with_font("测试")
        cond = {"font_name_cn": "宋体", "font_size_pt": None}  # 不检查字号
        issues = paragraph_style_executor(p, cond)
        # 只检查字体，不检查字号

    @pytest.mark.parametrize("align_actual, align_expected, should_pass", [
        (WD_ALIGN_PARAGRAPH.CENTER, "CENTER", True),
        (WD_ALIGN_PARAGRAPH.JUSTIFY, "CENTER", False),
        (WD_ALIGN_PARAGRAPH.LEFT, "LEFT", True),
    ])
    def test_alignment(self, docx_factory, align_actual, align_expected, should_pass):
        doc, p = docx_factory.create_paragraph_with_font("测试", alignment=align_actual)
        cond = {"alignment": align_expected}
        issues = paragraph_style_executor(p, cond)
        assert (len(issues) == 0) == should_pass


@pytest.mark.unit
class TestGlobalPropertyExecutor:

    def test_correct_a4_passes(self, docx_factory):
        doc = docx_factory.create_with_page_settings(width_cm=21.0, height_cm=29.7)
        cond = {"property": "page_width_cm", "expected": 21.0, "tolerance": 0.05, "compare": "equals"}
        issues = global_property_executor(doc.sections[0], cond)
        assert len(issues) == 0

    def test_wrong_paper_size_fails(self, docx_factory):
        doc = docx_factory.create_with_page_settings(width_cm=18.0)  # 非A4
        cond = {"property": "page_width_cm", "expected": 21.0, "tolerance": 0.05, "compare": "equals"}
        issues = global_property_executor(doc.sections[0], cond)
        assert len(issues) >= 1


@pytest.mark.unit
class TestRegexMatchExecutor:

    @pytest.mark.parametrize("text, pattern, mode, should_fail", [
        ("二〇二六年三月", r"[一二三四五六七八九〇]{4}年", "must_match", False),
        ("2026年3月", r"[一二三四五六七八九〇]{4}年", "must_match", True),
        ("本研究发现,结果显著", ",", "must_not_match", True),  # 英文逗号
        ("本研究发现，结果显著", ",", "must_not_match", False), # 中文逗号，OK
    ])
    def test_regex_matching(self, text, pattern, mode, should_fail):
        cond = {"pattern": pattern, "match_mode": mode}
        issues = regex_match_executor(text, cond)
        assert (len(issues) > 0) == should_fail


@pytest.mark.unit
class TestForbiddenWordsExecutor:

    def test_forbidden_word_found(self):
        text = "我认为这个结论是正确的"
        cond = {"inline_words": ["我认为", "我觉得"], "match_mode": "any"}
        issues = forbidden_words_executor(text, cond)
        assert len(issues) >= 1

    def test_clean_text_passes(self):
        text = "本研究表明该结论具有统计显著性"
        cond = {"inline_words": ["我认为", "我觉得"], "match_mode": "any"}
        issues = forbidden_words_executor(text, cond)
        assert len(issues) == 0

    def test_exception_zone_skipped(self):
        """致谢区域中允许使用第一人称"""
        text = "我由衷感谢我的导师"
        cond = {"inline_words": ["我"], "match_mode": "any", "exception_zones": ["acknowledgment"]}
        issues = forbidden_words_executor(text, cond, current_zone="acknowledgment")
        assert len(issues) == 0


@pytest.mark.unit
class TestCountCheckExecutor:

    def test_word_count_passes(self):
        text = "字" * 25000
        cond = {"count_type": "chinese_chars", "min_value": 20000}
        issues = count_check_executor(text, cond)
        assert len(issues) == 0

    def test_word_count_too_short(self):
        text = "字" * 5000
        cond = {"count_type": "chinese_chars", "min_value": 20000}
        issues = count_check_executor(text, cond)
        assert len(issues) >= 1
```

## 5.5 test_safe_annotator.py — 安全标注

```python
@pytest.mark.unit
class TestSafeAnnotator:

    def test_highlight_applied(self, zoned_doc):
        """验证黄色高亮被正确应用"""
        from safe_annotator import annotate_issue
        from docx.enum.text import WD_COLOR_INDEX
        issue = make_test_issue(paragraph_index=12)
        annotate_issue(zoned_doc, 12, [issue])
        for run in zoned_doc.paragraphs[12].runs:
            assert run.font.highlight_color == WD_COLOR_INDEX.YELLOW

    def test_annotation_paragraph_inserted(self, zoned_doc):
        """验证标注段落被插入到违规段落下方"""
        old_count = len(zoned_doc.paragraphs)
        issue = make_test_issue(paragraph_index=12)
        annotate_issue(zoned_doc, 12, [issue])
        # 应该多出一个标注段落
        new_count = len(list(zoned_doc.element.body.iterchildren()))
        assert new_count > old_count

    def test_multiple_issues_merged(self, zoned_doc):
        """同一段落的多条Issue合并为一个标注"""
        issues = [make_test_issue(paragraph_index=12, rule_id="R1"),
                  make_test_issue(paragraph_index=12, rule_id="R2")]
        annotate_issue(zoned_doc, 12, issues)
        # 只插入一个标注段落，包含两条建议

    def test_no_xml_comment_written(self, zoned_doc, tmp_docx):
        """核心红线测试：绝对不产生 <w:comment> XML节点"""
        issue = make_test_issue(paragraph_index=5)
        annotate_issue(zoned_doc, 5, [issue])
        zoned_doc.save(tmp_docx)
        # 解压docx检查XML
        import zipfile
        with zipfile.ZipFile(tmp_docx) as z:
            for name in z.namelist():
                content = z.read(name).decode("utf-8", errors="ignore")
                assert "w:comment" not in content, \
                    f"发现禁止的 w:comment 节点在 {name} 中！违反 Req-7！"

    def test_saved_docx_opens_without_error(self, zoned_doc, tmp_docx):
        """标注后的docx文件可以被python-docx正常重新打开"""
        issue = make_test_issue(paragraph_index=5)
        annotate_issue(zoned_doc, 5, [issue])
        zoned_doc.save(tmp_docx)
        reopened = Document(tmp_docx)  # 不报错即通过
        assert len(reopened.paragraphs) > 0
```

## 5.6 test_claude_engine.py — Claude引擎（全Mock）

```python
@pytest.mark.unit
class TestClaudeEngine:

    def test_skipped_when_no_api_key(self):
        """无API Key时gracefully跳过"""
        result = claude_engine.run(doc=None, zone_map={}, rules=[], api_key=None)
        assert result == []  # 空结果，不报错

    def test_skipped_when_no_claude_rules(self, mock_claude_response):
        """没有ai_semantic规则时不调用API"""
        result = claude_engine.run(doc=None, zone_map={}, rules=[], api_key="test-key")
        assert result == []
        mock_claude_response.return_value.messages.create.assert_not_called()

    def test_returns_issues_on_valid_response(self, zoned_doc, mock_claude_response):
        """Claude返回有效JSON时生成Issue"""
        rules = [{"rule_id": "SEM_01", "check_type": "ai_semantic",
                  "target_zone": ["abstract_cn"],
                  "conditions": {"prompt_template": "检查摘要...{text}"},
                  "error_message": "摘要缺少要素", "enabled": True}]
        zone_map = {4: "abstract_cn", 5: "abstract_cn"}
        result = claude_engine.run(zoned_doc, zone_map, rules, "test-key")
        assert len(result) >= 0  # 根据mock返回判断

    def test_timeout_graceful(self, mocker):
        """API超时不崩溃"""
        import anthropic
        mocker.patch("anthropic.Anthropic").return_value.messages.create.side_effect = \
            anthropic.APITimeoutError("timeout")
        result = claude_engine.run(None, {}, [{"rule_id": "X", "check_type": "ai_semantic",
            "target_zone": ["abstract_cn"], "conditions": {}, "error_message": "", "enabled": True}], "key")
        assert result == []  # 超时返回空，不crash
```

## 5.7 test_issue_merger.py — Issue合并

```python
@pytest.mark.unit
class TestIssueMerger:

    def test_group_by_paragraph(self):
        issues = [
            Issue(rule_id="R1", paragraph_index=5, zone="body", engine="Python",
                  urgency="★★★★★", message="错误1"),
            Issue(rule_id="R2", paragraph_index=5, zone="body", engine="Python",
                  urgency="★★★★☆", message="错误2"),
            Issue(rule_id="R3", paragraph_index=10, zone="body", engine="Python",
                  urgency="★★★★★", message="错误3"),
        ]
        groups = group_by_paragraph(issues)
        assert len(groups[5]) == 2
        assert len(groups[10]) == 1

    def test_dedup_same_rule_same_paragraph(self):
        """同一段落同一规则不重复"""
        issues = [
            Issue(rule_id="R1", paragraph_index=5, zone="body", engine="Python",
                  urgency="★★★★★", message="错误1"),
            Issue(rule_id="R1", paragraph_index=5, zone="body", engine="Claude",
                  urgency="★★★★★", message="错误1"),  # 双擎重复
        ]
        merged = merge_issues(issues)
        r1_at_5 = [i for i in merged if i.rule_id == "R1" and i.paragraph_index == 5]
        assert len(r1_at_5) == 1
```

---

# 六、L2 集成测试详细规范

## 6.1 test_md_to_registry.py — MD→规则库→覆盖率 全链路

```python
@pytest.mark.integration
class TestMdToRegistry:

    def test_full_md_parses_164_rules(self):
        """用真实MD清单验证解析出的规则数"""
        rules = parse_md_to_rules("EMBA论文格式排版要求清单_补充完善版.md")
        assert len(rules) >= 160  # 允许小幅波动，但不应大幅偏离164

    def test_coverage_100_percent(self, tmp_path):
        """解析后的规则库通过覆盖率核对"""
        rules = parse_md_to_rules("EMBA论文格式排版要求清单_补充完善版.md")
        registry_path = tmp_path / "rules.json"
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(rules, f, ensure_ascii=False)
        missing, orphan = run_coverage_check(
            "EMBA论文格式排版要求清单_补充完善版.md", str(registry_path))
        assert len(missing) == 0, f"MD中有但规则库缺失: {missing}"
        assert len(orphan) == 0, f"规则库中有但MD缺失: {orphan}"

    def test_all_rules_have_valid_check_type(self):
        """所有规则的check_type不为unknown（定稿后）"""
        rules = parse_md_to_rules("EMBA论文格式排版要求清单_补充完善版.md")
        valid_types = {"paragraph_style", "global_property", "regex_match",
                       "count_check", "cross_reference", "text_match",
                       "forbidden_words", "ai_semantic", "unknown"}
        for r in rules:
            assert r["check_type"] in valid_types, f"{r['rule_id']} has invalid type"
```

## 6.2 test_engine_pipeline.py — 引擎管线集成

```python
@pytest.mark.integration
class TestEnginePipeline:

    def test_zone_detection_feeds_engine(self, zoned_doc, sample_rules):
        """zone_map 正确传递给引擎，zone不匹配的规则不触发"""
        zone_map = detect_zones(zoned_doc)
        issues = docx_engine.run(zoned_doc, zone_map, sample_rules)
        # body_chapter规则不应在cover区触发
        cover_issues = [i for i in issues if i.zone == "cover" and "BODY" in i.rule_id]
        assert len(cover_issues) == 0

    def test_error_doc_triggers_issues(self, error_doc, sample_rules):
        """故意错误文档应触发Issue"""
        zone_map = detect_zones(error_doc)
        issues = docx_engine.run(error_doc, zone_map, sample_rules)
        assert len(issues) > 0

    def test_single_rule_error_doesnt_crash_others(self, zoned_doc, sample_rules):
        """一条规则执行失败不影响其他规则"""
        # 注入一条必定报错的坏规则
        bad_rule = {"rule_id": "BAD_01", "check_type": "paragraph_style",
                    "target_group": "Group2_Paragraphs", "target_zone": ["body_chapter"],
                    "engine": "Python", "conditions": {"font_size_pt": "not_a_number"},  # 故意错误
                    "error_message": "坏规则", "enabled": True, "urgency": "★★★★★"}
        rules = sample_rules + [bad_rule]
        zone_map = detect_zones(zoned_doc)
        # 不应抛出异常
        issues = docx_engine.run(zoned_doc, zone_map, rules)
        # 其他规则仍正常执行
```

## 6.3 test_annotator_docx.py — 标注→文件完整性

```python
@pytest.mark.integration
class TestAnnotatorDocxIntegrity:

    def test_annotated_docx_roundtrip(self, error_doc, sample_rules, tmp_docx):
        """标注后的docx可以保存→重新打开→再标注"""
        zone_map = detect_zones(error_doc)
        issues = docx_engine.run(error_doc, zone_map, sample_rules)
        grouped = group_by_paragraph(issues)
        for para_idx, issue_list in grouped.items():
            annotate_issue(error_doc, para_idx, issue_list)
        error_doc.save(tmp_docx)
        # 重新打开不报错
        doc2 = Document(tmp_docx)
        assert len(doc2.paragraphs) > 0

    def test_no_xml_corruption_after_annotation(self, error_doc, sample_rules, tmp_docx):
        """标注后的docx XML结构完整"""
        zone_map = detect_zones(error_doc)
        issues = docx_engine.run(error_doc, zone_map, sample_rules)
        grouped = group_by_paragraph(issues)
        for para_idx, issue_list in grouped.items():
            annotate_issue(error_doc, para_idx, issue_list)
        error_doc.save(tmp_docx)
        # 验证zip结构完整
        import zipfile
        assert zipfile.is_zipfile(tmp_docx)
        with zipfile.ZipFile(tmp_docx) as z:
            assert z.testzip() is None  # 无损坏
            assert "word/document.xml" in z.namelist()
```

---

# 七、L3 端到端测试详细规范

## 7.1 test_full_pipeline.py — 完整管线

```python
@pytest.mark.e2e
class TestFullPipeline:

    def test_compliant_doc_zero_issues(self, tmp_path):
        """合规文档应产生0个Issue（或仅skip类提示）"""
        input_docx = create_fully_compliant_docx(tmp_path)  # fixture
        output_docx, output_txt = run_full_check(
            input_path=str(input_docx),
            md_path="EMBA论文格式排版要求清单_补充完善版.md",
            api_key=None,  # 不用Claude
            output_dir=str(tmp_path)
        )
        assert os.path.exists(output_docx)
        assert os.path.exists(output_txt)
        with open(output_txt, "r", encoding="utf-8") as f:
            report = f.read()
        # 只应有skip提示，不应有格式错误
        assert "格式不符" not in report or "跳过" in report

    def test_error_doc_produces_issues_and_annotations(self, tmp_path):
        """错误文档应产生Issue，输出文件包含标注"""
        doc = DocxFactory.create_with_errors()
        input_path = str(tmp_path / "input.docx")
        doc.save(input_path)
        output_docx, output_txt = run_full_check(
            input_path=input_path,
            md_path="EMBA论文格式排版要求清单_补充完善版.md",
            api_key=None,
            output_dir=str(tmp_path)
        )
        # 审查报告中应有问题
        with open(output_txt, "r", encoding="utf-8") as f:
            report = f.read()
        assert "问题" in report or "Issue" in report
        # 输出docx中应有黄色高亮
        result_doc = Document(output_docx)
        highlighted = any(
            run.font.highlight_color is not None
            for p in result_doc.paragraphs for run in p.runs
        )
        assert highlighted, "输出文档中应有黄色高亮标注"

    def test_empty_doc_no_crash(self, tmp_path):
        """空白文档不崩溃"""
        doc = Document()
        input_path = str(tmp_path / "empty.docx")
        doc.save(input_path)
        output_docx, output_txt = run_full_check(
            input_path=input_path,
            md_path="EMBA论文格式排版要求清单_补充完善版.md",
            api_key=None,
            output_dir=str(tmp_path)
        )
        assert os.path.exists(output_docx)
        assert os.path.exists(output_txt)

    def test_original_file_untouched(self, tmp_path):
        """Req-7：原文件绝对不被修改"""
        doc = DocxFactory.create_with_errors()
        input_path = str(tmp_path / "original.docx")
        doc.save(input_path)
        import hashlib
        with open(input_path, "rb") as f:
            hash_before = hashlib.md5(f.read()).hexdigest()
        run_full_check(input_path=input_path,
            md_path="EMBA论文格式排版要求清单_补充完善版.md",
            api_key=None, output_dir=str(tmp_path))
        with open(input_path, "rb") as f:
            hash_after = hashlib.md5(f.read()).hexdigest()
        assert hash_before == hash_after, "原文件被修改了！违反Req-7！"

    def test_output_naming_convention(self, tmp_path):
        """输出文件命名规范：{原文件名}_审查结果_{timestamp}.docx"""
        doc = Document()
        doc.add_paragraph("test")
        input_path = str(tmp_path / "张三_EMBA论文.docx")
        doc.save(input_path)
        output_docx, output_txt = run_full_check(
            input_path=input_path,
            md_path="EMBA论文格式排版要求清单_补充完善版.md",
            api_key=None, output_dir=str(tmp_path))
        assert "张三_EMBA论文_审查结果_" in os.path.basename(output_docx)
        assert "张三_EMBA论文_审查报告_" in os.path.basename(output_txt)
```

## 7.2 test_gui_flow.py — GUI 无头测试

```python
@pytest.mark.e2e
class TestGuiFlow:
    """
    Tkinter GUI 无头测试策略：
    不启动真实GUI窗口，而是直接调用GUI组件的回调函数，
    验证状态变化和输出结果。
    """

    def test_start_button_triggers_check(self, mocker, tmp_path):
        """点击开始按钮触发检查流程"""
        mock_orchestrator = mocker.patch("orchestrator.run_full_check")
        mock_orchestrator.return_value = ("out.docx", "out.txt")

        # 直接调用GUI的回调函数，不创建窗口
        from gui import CheckApp
        app = CheckApp.__new__(CheckApp)  # 不调用__init__避免创建Tk窗口
        app.input_path = str(tmp_path / "test.docx")
        app.md_path = "EMBA论文格式排版要求清单_补充完善版.md"
        app.api_key = ""
        app.check_level = "all"
        app.claude_enabled = False
        
        # 模拟回调
        app._on_check_complete = mocker.MagicMock()
        app._run_check_thread()
        mock_orchestrator.assert_called_once()

    def test_claude_toggle_off_skips_claude(self, mocker):
        """Claude开关关闭时不传API Key"""
        mock_orch = mocker.patch("orchestrator.run_full_check")
        mock_orch.return_value = ("out.docx", "out.txt")

        from gui import CheckApp
        app = CheckApp.__new__(CheckApp)
        app.claude_enabled = False
        app.api_key = "sk-test-key"  # 即使有key
        app._run_check_thread()
        # 调用时api_key应为None
        call_kwargs = mock_orch.call_args
        assert call_kwargs is not None
        # 验证传入的api_key为None（因为开关关闭）
```

---

# 八、红线要求专项测试矩阵

PRD 的 7 条红线要求，每条至少有 1 个直接验证的测试用例：

| 红线 | 测试文件 | 测试用例 | 验证方式 |
|------|---------|---------|---------|
| Req-1 MD清单驱动 | test_md_to_registry.py | test_full_md_parses_164_rules | 规则数断言 |
| Req-2 黄色高亮+标注 | test_safe_annotator.py | test_highlight_applied, test_annotation_paragraph_inserted | docx属性检查 |
| Req-3 规则库先行 | test_engine_pipeline.py | test_zone_detection_feeds_engine | 不存在硬编码if-else |
| Req-4 分组遍历 | test_docx_engine.py | test_groups_execute_in_order | Group执行顺序断言 |
| Req-5 覆盖率100% | test_md_to_registry.py | test_coverage_100_percent | 双向差集为空 |
| Req-6 双擎独立 | test_claude_engine.py | test_skipped_when_no_api_key | Claude关闭时不crash |
| Req-7 禁止XML批注 | test_safe_annotator.py | test_no_xml_comment_written | 解压docx检查XML |
| Req-7 原文件不动 | test_full_pipeline.py | test_original_file_untouched | MD5前后比对 |

---

# 九、执行步骤

**按以下顺序实现测试，每完成一批停下来让我确认：**

### Step T1: 基础设施
1. 创建 `tests/` 目录结构
2. 创建 `tests/pytest.ini`
3. 创建 `tests/conftest.py`（包含 DocxFactory 和所有 fixture）
4. 更新 `requirements.txt` 追加 pytest 依赖
5. 验证：`pytest --collect-only` 不报错

### Step T2: L1 单元测试
1. 按第五部分规范，为每个模块编写单元测试
2. **优先级**：test_rule_executors.py > test_zone_detector.py > test_safe_annotator.py > test_md_parser.py > 其余
3. 验证：`pytest -m unit` 全部通过

### Step T3: L2 集成测试
1. 按第六部分规范编写
2. 验证：`pytest -m integration` 全部通过

### Step T4: L3 E2E 测试
1. 按第七部分规范编写
2. 验证：`pytest -m e2e` 全部通过

### Step T5: 覆盖率达标
1. 运行 `pytest --cov=emba_checker --cov-report=html --cov-fail-under=85`
2. 如果覆盖率不足，补充测试用例
3. 输出覆盖率报告截图/数据

---

> **开始执行 Step T1。每步完成后停下来告诉我交付物和结果。**