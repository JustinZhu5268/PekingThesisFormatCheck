# 北大光华 EMBA 论文格式自动化审查工具 — 产品需求文档 (PRD)
## 双擎规则驱动 · 工程化终极版

> **版本**: 2.0 Final
> **日期**: 2026年3月3日
> **目标读者**: Cursor AI 编程助手
> **配套文件**: `EMBA论文格式排版要求清单完善版.md`（以下简称"MD清单"）

---

# 第一部分：总纲

## 1. 产品概述

本文档指导 Cursor 开发一款带极简 GUI 的本地 Python 桌面应用，用于自动审查 `.docx` 格式的北大光华 EMBA 学位论文。
程序读取 MD 清单中的 **164 条**可编程规则（其中 136 条全自动 + 28 条半自动），对论文文档逐项检查，生成带标注的审查结果文档和审查报告。

## 2. 七条不可逾越的红线要求

以下 7 条要求贯穿全部设计，**任何模块的实现都不得与之矛盾**：

| 红线编号 | 要求 | 落实章节 |
|---------|------|---------|
| **Req-1** | 基于 MD 清单生成自动检查工具 | 第三部分(规则库) + 附录A(164条映射) |
| **Req-2** | 黄色高亮违规处 + 旁侧红色加粗标注修改建议；优先在违规段落下方插入独立标注段落，而非淹没在段尾 | 第八部分(安全标注) |
| **Req-3** | 规则库先行，禁止业务代码硬编码 if-else | 第三部分(规则库设计) |
| **Req-4** | 同类规则分组遍历，最少遍历次数 | 第六部分(分组遍历) |
| **Req-5** | 自动化双向核对：MD ↔ 规则库 100% 覆盖，否则拒绝启动 | 第四部分(覆盖率核对) |
| **Req-6** | 极简 GUI + Claude Sonnet 4.5 API 处理语义校验 + 双擎独立运行、结果合并 | 第七部分(双擎) + 第九部分(GUI) |
| **Req-7** | 零风险容忍：绝对禁止 XML 写入批注 `<w:comment>`，安全降级链保障文档不损坏 | 第八部分(降级链) |

## 3. AI 引擎选型：Claude Sonnet 4.5

### 3.1 选型对比

| 维度 | Gemini 2.5 Pro | Claude Sonnet 4.5 | Claude Opus 4.5 |
|------|---------------|-------------------|-----------------|
| 中文学术语义理解 | 良好 | **优秀** | 极优秀 |
| 结构化指令遵循(JSON输出) | 中等(易跑题) | **极强** | 极强 |
| 中文标点/格式敏感度 | 一般 | **极高** | 极高 |
| 响应速度 | 快 | **快** | 慢(3-5倍) |
| 成本(每百万输入token) | ~$1.25 | **~$3** | ~$15 |
| 本场景推荐度 | 不推荐 | **推荐** | 过剩 |

### 3.2 推荐结论

**选用 Claude Sonnet 4.5**（`claude-sonnet-4-5-20250929`）。

本场景的 AI 任务属于"规则明确的判断型任务"（判断摘要是否包含四要素、段落是否口语化、翻译是否一致等），
不需要深度开放式推理。Sonnet 在结构化输出和中文理解上与 Opus 持平，但速度快 3 倍、成本低 5 倍。
Opus 适合需要极深推理链的复杂分析场景，此处属于杀鸡用牛刀。

### 3.3 API 调用示例

```python
import anthropic

client = anthropic.Anthropic(api_key=user_provided_key)
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=2000,
    system="你是北大光华EMBA论文格式审查专家。请严格按JSON格式输出审查结果。",
    messages=[{"role": "user", "content": prompt}]
)
result_text = response.content[0].text
```

依赖包：`pip install anthropic>=0.39.0`

---

# 第二部分：系统架构

## 4. 模块总览

```
┌─────────────────────────────────────────────────────────┐
│                    AppGUI (Tkinter)                      │
│  文件选择 · API Key · 检查级别 · 进度条 · 结果摘要 · 日志 │
└────────────────────────┬────────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │   Orchestrator      │ ← 总调度器
              └──┬───┬───┬───┬──┬──┘
                 │   │   │   │  │
    ┌────────────▼┐ ┌▼───▼┐ ┌▼──▼────────────┐
    │Coverage     │ │Zone  │ │ Safe           │
    │Validator    │ │Detect│ │ Annotator      │
    └─────────────┘ └──┬──┘ └────────────────┘
              ┌────────▼────────┐
              │  Rule_Registry  │ ← 唯一事实标准(164条)
              └────────┬────────┘
          ┌────────────┼────────────┐
          ▼                         ▼
   ┌─────────────┐          ┌─────────────┐
   │ Docx_Engine │          │Claude_Engine│
   │ (Python)    │          │ (可选,异步)  │
   └──────┬──────┘          └──────┬──────┘
          └────────────┬───────────┘
              ┌────────▼────────┐
              │  Issue Merger   │ ← 合并+去重
              └─────────────────┘
```

## 5. 文件结构

```
emba_checker/
├── main.py                    # 入口，启动 GUI
├── config.py                  # 配置常量（路径、版本、默认值）
├── md_parser.py                # MD清单解析器：自动提取规则（Req-3 核心）
├── generate_registry.py       # 规则库生成器：MD→JSON（可选Claude NLP辅助）
├── rules_registry.json        # 164条结构化规则（由generate_registry.py自动生成，禁止手写）
├── verify_coverage.py         # 独立脚本：MD↔规则库双向核对（Req-5）
├── zone_detector.py           # 区域识别模块
├── docx_engine.py             # Python 确定性检查引擎（Req-4）
├── rule_executors.py          # 7种check_type的执行器实现
├── claude_engine.py           # Claude Sonnet 4.5 语义引擎（Req-6）
├── safe_annotator.py          # 安全标注 + 降级链（Req-2 & Req-7）
├── issue_merger.py            # 双擎结果合并去重
├── orchestrator.py            # 主控调度流程
├── gui.py                     # Tkinter 界面（Req-6）
├── utils.py                   # 工具函数（单位换算、正则库、XML安全读取）
├── word_lists/                # 词库目录
│   ├── forbidden_words.txt    # 禁用词（百度百科、粗俗词等）
│   ├── colloquial_words.txt   # 口语化词库
│   ├── research_directions.txt # 27个指定研究方向
│   └── copyright_template.txt # 版权声明标准文本
├── tests/
│   ├── test_compliant.docx    # 合规模板（期望 0 issue）
│   ├── test_errors.docx       # 故意错误（期望触发多条规则）
│   └── test_empty.docx        # 空白文档（期望不 crash）
└── requirements.txt           # python-docx>=0.8.11, anthropic>=0.39.0, lxml
```

## 6. 技术依赖与环境

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | >= 3.10 | 运行环境 |
| python-docx | >= 0.8.11 | docx读写 |
| lxml | >= 4.9 | 安全读取XML（页眉/脚注/域代码，**只读不写**） |
| anthropic | >= 0.39.0 | Claude API（可选） |
| tkinter | 内置 | GUI |
| re / json / os / shutil / datetime / threading | 内置 | 基础工具 |

---

# 第三部分：结构化规则库设计 (落实 Req-3)

## 7. 核心原则

**`rules_registry.json` 是系统的唯一事实标准（Single Source of Truth）。**

所有检查逻辑必须从此文件读取，禁止在 `docx_engine.py` 或任何业务代码中硬编码 `if font_name == '黑体'` 之类的判断。
业务代码只实现 7 种通用的 `check_type` 执行器，规则库提供具体参数。

## 8. 规则结构定义

每条规则必须包含以下字段：

```json
{
  "rule_id": "COVER_01",
  "md_source": "一、封面页格式 - 论文题目（主标题）",
  "md_source_key": "一、封面页格式::论文题目（主标题）",
  "automation_level": "auto",
  "urgency": "★★★★★",
  "target_group": "Group2_Paragraphs",
  "target_zone": ["cover"],
  "engine": "Python",
  "check_type": "paragraph_style",
  "conditions": {
    "font_name_cn": "黑体",
    "font_size_pt": 26,
    "bold": true,
    "alignment": "CENTER",
    "max_char_count": 20
  },
  "error_message": "封面主标题必须为黑体一号(26pt)、加粗、居中，且不超过20个汉字。",
  "enabled": true
}
```

### 8.1 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `rule_id` | string | 唯一标识，格式 `{前缀}_{序号}`，见附录A |
| `md_source` | string | 规则在MD清单中的出处（章节 - 要素） |
| `md_source_key` | string | 双向核对用复合Key：`"{章节}::{要素}"`，解决同名要素冲突 |
| `automation_level` | enum | `auto`(全自动) 或 `semi`(半自动) |
| `urgency` | string | 紧急程度（原样保留星级） |
| `target_group` | enum | 遍历分组，见第六部分 |
| `target_zone` | list[string] | 规则生效的文档区域，见第五部分 |
| `engine` | enum | `Python` / `Claude` / `Python+Claude` / `Python+Manual` |
| `check_type` | enum | 7种检查类型之一，见8.2节 |
| `conditions` | object | 检查参数，结构因 `check_type` 而异 |
| `error_message` | string | 违规时的中文提示信息 |
| `enabled` | bool | 是否启用（允许用户在GUI中按紧急程度批量开关） |

### 8.2 七种 check_type 及其 conditions 模板

Cursor 必须为以下 7 种类型分别实现一个通用执行器函数（在 `rule_executors.py` 中）。
每种执行器接收 `(element, conditions)` 参数，返回 `list[Issue]`。

#### 类型 1: `paragraph_style` — 段落样式检查

适用场景：检查段落的字体、字号、对齐、缩进、行距、段前段后间距等。
覆盖规则举例：章标题字体、摘要正文格式、参考文献字号等。

```json
{
  "check_type": "paragraph_style",
  "conditions": {
    "style_name_contains": null,
    "font_name_cn": "宋体",
    "font_name_en": "Times New Roman",
    "font_size_pt": 12,
    "bold": false,
    "italic": false,
    "alignment": "JUSTIFY",
    "line_spacing_type": "MULTIPLE",
    "line_spacing_value": 1.25,
    "space_before_pt": 0,
    "space_after_pt": 0,
    "first_line_indent_char": 2,
    "hanging_indent_char": null
  }
}
```

**执行逻辑**：对段落的每个 run 检查字体属性，对段落格式检查缩进/对齐/行距。
`null` 表示不检查该项。若 `font_name_cn` 和 `font_name_en` 同时指定，则中文字符检查 cn 字体、ASCII字符检查 en 字体。

#### 类型 2: `global_property` — 全局/节属性检查

适用场景：页面尺寸、页边距、页眉页脚边距等文档级属性。

```json
{
  "check_type": "global_property",
  "conditions": {
    "property": "page_width_cm",
    "expected": 21.0,
    "tolerance": 0.05,
    "compare": "equals"
  }
}
```

**执行逻辑**：读取 `doc.sections[i]` 的对应属性（需单位换算：EMU→cm/pt），与 expected 比较。
`compare` 可为 `equals`/`gte`/`lte`。`tolerance` 为允许误差。

**property 枚举值**：`page_width_cm`, `page_height_cm`, `top_margin_cm`, `bottom_margin_cm`, `left_margin_cm`, `right_margin_cm`, `header_distance_cm`, `footer_distance_cm`, `gutter_cm`

#### 类型 3: `regex_match` — 正则匹配检查

适用场景：日期格式、图表编号、引用格式、标点检测等。

```json
{
  "check_type": "regex_match",
  "conditions": {
    "pattern": "[一二三四五六七八九〇]{4}年[一二三四五六七八九十]{1,2}月",
    "match_mode": "must_match",
    "scope": "full_text",
    "case_sensitive": false
  }
}
```

**match_mode**：
- `must_match`：段落文本必须匹配该正则（如日期格式）
- `must_not_match`：段落文本不得匹配该正则（如禁止英文标点出现在中文正文中）
- `find_all_violations`：找出所有匹配位置并逐一报告（如找出所有英文逗号）

**scope**：`full_text`（整段文本）/ `each_run`（逐run检查）/ `first_line`（仅首行）

#### 类型 4: `count_check` — 计数/统计检查

适用场景：正文字数、摘要字数、关键词个数、参考文献数量等。

```json
{
  "check_type": "count_check",
  "conditions": {
    "count_type": "chinese_chars",
    "min_value": 20000,
    "max_value": null,
    "target_scope": "zone"
  }
}
```

**count_type 枚举**：`chinese_chars`（中文字符数）, `total_chars`, `paragraphs`, `keywords`（逗号分隔的关键词数）, `references`（参考文献条目数）, `pages`

#### 类型 5: `cross_reference` — 交叉引用检查

适用场景：图表编号与正文引用一一对应、参考文献列表与正文引用对应。

```json
{
  "check_type": "cross_reference",
  "conditions": {
    "caption_pattern": "图\\s*\\d+\\.\\d+",
    "caption_zone": ["body_chapter"],
    "reference_pattern": "(?:见|如|参见)\\s*图\\s*\\d+\\.\\d+",
    "reference_zone": ["body_chapter"],
    "error_on": "caption_without_reference"
  }
}
```

**error_on**：`caption_without_reference`（有图但正文没引用）/ `reference_without_caption`（正文引用了但没有图）/ `both`

#### 类型 6: `text_match` — 文本精确匹配/包含检查

适用场景：版权声明固定文本、特定标题文字（"摘要""ABSTRACT""目录"等）。

```json
{
  "check_type": "text_match",
  "conditions": {
    "expected_text": "任何收存和保管本论文各种版本的单位和个人...",
    "match_mode": "exact",
    "normalize_whitespace": true
  }
}
```

**match_mode**：`exact`（逐字比对，去除首尾空白）/ `contains`（包含即可）/ `starts_with` / `not_contains`

#### 类型 7: `forbidden_words` — 禁用词/词库检查

适用场景：禁止引用百度百科、禁止口语化表达、禁止第一人称等。

```json
{
  "check_type": "forbidden_words",
  "conditions": {
    "word_list_file": "colloquial_words.txt",
    "inline_words": ["我认为", "我觉得", "众所周知"],
    "match_mode": "any",
    "exception_zones": ["acknowledgment"]
  }
}
```

**word_list_file**：从 `word_lists/` 目录读取，每行一个词。
**inline_words**：直接内联的词表（少量时使用）。两者取并集。
**exception_zones**：在这些区域中不触发（如致谢区可以用"我"）。

#### 特殊类型: `ai_semantic` — Claude 语义检查

适用场景：摘要四要素、翻译一致性、段落连贯性等 Python 无法判断的语义任务。

```json
{
  "check_type": "ai_semantic",
  "conditions": {
    "prompt_template": "请检查以下中文摘要是否包含研究目的、方法、结果、结论四要素。\n摘要内容：{text}\n请以JSON格式回答：{format_spec}",
    "format_spec": {"has_purpose":true,"has_method":true,"has_result":true,"has_conclusion":true,"missing_elements":[],"suggestion":""},
    "max_text_length": 3000,
    "batch_mode": "by_zone"
  }
}
```

**batch_mode**：`by_zone`（整个区域一次发送）/ `by_paragraph`（逐段发送，慎用）/ `by_chapter`（逐章发送）

---

# 第四部分：自动化覆盖率核对 (落实 Req-5)

## 9. verify_coverage.py 规格

**这是项目的核心质控环节，必须在主程序启动前通过。**

### 9.1 工作流程

```
1. 读取 MD 清单文件
2. 用正则解析所有 Markdown 表格行
3. 提取「可编程性」列包含 ✅ 或 ⚠️ 的行
4. 生成 md_keys 集合，Key 格式："{章节名}::{要素名}"
5. 读取 rules_registry.json
6. 生成 registry_keys 集合，取每条规则的 md_source_key
7. 计算差集：
   - missing_in_registry = md_keys - registry_keys（MD有但规则库没有）
   - orphan_in_registry = registry_keys - md_keys（规则库有但MD没有）
8. 如果两个差集都为空 → 通过，输出 "覆盖率核对通过：164/164"
9. 如果不为空 → 报错并列出清单，写入 coverage_report.txt，拒绝启动主程序
```

### 9.2 为什么用复合 Key

MD 中有多个同名要素（如"编号规则"出现在图、表、公式三处，"正文引用"出现在图、表、参考文献三处，"行距"出现在三处）。
仅用要素名做 Key 会冲突。复合 Key 格式：`"{章节全名}::{要素名}"`。

示例：
- `"11.1 图的要求::编号规则"`
- `"11.2 表的要求::编号规则"`
- `"十二、表达式（公式）格式::编号规则"`

### 9.3 阻断机制

```python
def verify_and_block(md_path, registry_path):
    """启动前调用。覆盖率不足则 raise SystemExit"""
    missing, orphan = run_coverage_check(md_path, registry_path)
    if missing or orphan:
        report = generate_report(missing, orphan)
        with open('coverage_report.txt', 'w') as f:
            f.write(report)
        raise SystemExit(f"覆盖率核对失败！详见 coverage_report.txt")
    return True
```

---

# 第五部分：区域识别机制 (Zone Detection)

## 10. 为什么需要区域识别

同一条规则在不同区域的适用性不同：
- "必须使用中文标点" → 在正文中触发，在英文摘要和参考文献中**不触发**
- "宋体小四" → 在中文摘要中触发，在封面中**不触发**（封面用黑体一号）
- "禁止第一人称" → 在正文中触发，在致谢中**不触发**

没有区域标签，规则就会乱判，产生大量误报。

## 11. 区域定义

```python
ZONES = [
    "cover",            # 封面（文档开头到"版权声明"之前）
    "copyright",        # 版权声明页
    "declaration",      # 原创性声明 + 授权说明 + 承诺书
    "abstract_cn",      # 中文摘要（从"摘要"到"ABSTRACT"之前）
    "abstract_en",      # 英文摘要（从"ABSTRACT"到"目录"之前）
    "toc",              # 目录（从"目录"到"第一章"之前）
    "body_chapter",     # 正文章节（从"第一章"到"参考文献"之前，可细分为 body_chapter_1, 2, ...）
    "references",       # 参考文献
    "appendix",         # 附录
    "acknowledgment",   # 致谢
]
```

## 12. 实现方式

```python
# zone_detector.py 核心逻辑伪代码
def detect_zones(doc) -> dict[int, str]:
    """
    遍历 doc.paragraphs，根据特征文本和样式标记每个段落的 zone。
    返回 {paragraph_index: zone_name}
    """
    zone_map = {}
    current_zone = "cover"
    
    # 分界标志（按优先级从后往前定义）
    markers = [
        # (特征文本/正则, 段落样式条件, 切换到的zone)
        ("版权声明", None, "copyright"),
        ("原创性声明", None, "declaration"),
        (r"^摘\s*要$", "Heading", "abstract_cn"),
        (r"^ABSTRACT$", "Heading", "abstract_en"),
        (r"^目\s*录$", "Heading", "toc"),
        (r"^第[一二三四五六七八九十]+章", "Heading", "body_chapter"),
        (r"^参考文献$", "Heading", "references"),
        (r"^附录", "Heading", "appendix"),
        (r"^致\s*谢$", "Heading", "acknowledgment"),
    ]
    
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        for pattern, style_hint, zone_name in markers:
            if re.match(pattern, text):
                if style_hint is None or (para.style and style_hint in para.style.name):
                    current_zone = zone_name
                    break
        zone_map[i] = current_zone
    
    return zone_map
```

**关键要求**：zone_detector 必须在所有引擎遍历之前运行完毕，其结果作为只读参数传入各引擎。

---

# 第六部分：分组遍历策略 (落实 Req-4)

## 13. 分组原则

同一类型的文档元素只遍历一次。遍历时，触发该 Group 下的所有规则。
6 个 Group 按顺序执行，每个 Group 结束后汇报发现的 Issue 数量。

## 14. 六个 Group 定义

### Group 1: Global (全局属性) — 不遍历段落

| 遍历对象 | 触发规则示例 | 规则数 |
|---------|------------|--------|
| `doc.sections` | 纸张A4、页边距、页眉页脚距边界、装订线 | ~4 |

### Group 1B: HeaderFooter (页眉页脚) — 遍历 sections 的 header/footer

| 遍历对象 | 触发规则示例 | 规则数 |
|---------|------------|--------|
| `section.header`, `section.footer` | 页眉字体、页眉内容、页码字体、页码位置、奇偶页设置 | ~9 |

**技术说明**：python-docx 对页眉页脚的支持有限，部分属性（如奇偶页不同的内容、页码格式域代码）需要通过 lxml 安全读取底层 XML。**只读XML是安全的，禁止的是写入XML。**

```python
# 安全读取页眉XML示例
from lxml import etree
header_xml = section.header._element  # 只读访问
runs = header_xml.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r')
```

### Group 2: Paragraphs (段落与文本) — 核心遍历，覆盖最多规则

| 遍历对象 | 触发规则分类 | 规则数 |
|---------|------------|--------|
| `doc.paragraphs` + zone_map | 封面格式、版权声明、摘要格式、目录格式、正文标题、正文段落、标点、公式、附录、致谢、文字规范 | ~100+ |

**遍历伪代码**：

```python
def run_group2(doc, zone_map, rules_by_group):
    group2_rules = rules_by_group["Group2_Paragraphs"]
    issues = []
    for i, para in enumerate(doc.paragraphs):
        zone = zone_map[i]
        # 筛选出在当前 zone 生效的规则
        active_rules = [r for r in group2_rules
                        if zone_matches(zone, r['target_zone'])]
        for rule in active_rules:
            executor = get_executor(rule['check_type'])
            result = executor(para, rule['conditions'])
            if result:
                issues.append(Issue(
                    rule_id=rule['rule_id'],
                    paragraph_index=i,
                    message=rule['error_message'],
                    engine='Python',
                    zone=zone
                ))
    return issues
```

### Group 3: Tables & Figures (图表) — 遍历表格和内联图

| 遍历对象 | 触发规则示例 | 规则数 |
|---------|------------|--------|
| `doc.tables`, `doc.inline_shapes`, 图表前后段落 | 图表编号格式、题注位置、表格字体、资料来源、续表 | ~23 |

### Group 4: Footnotes (脚注) — 通过 XML 安全读取

| 遍历对象 | 触发规则示例 | 规则数 |
|---------|------------|--------|
| `doc.part.footnotes_part` (lxml只读) | 脚注字体、缩进、行距、序号、网址标注 | ~7 |

**技术说明**：python-docx 没有原生 footnotes API，必须通过 lxml 读取 `word/footnotes.xml`。这是安全的只读操作。

```python
# 安全读取脚注
footnotes_part = doc.part.rels.get('rId_footnotes')  # 或直接读取 part
if footnotes_part:
    footnotes_xml = etree.fromstring(footnotes_part.blob)
    # ... 解析 footnote 元素
```

### Group 5: References (参考文献) — 定位后集中处理

| 遍历对象 | 触发规则示例 | 规则数 |
|---------|------------|--------|
| zone='references' 的段落 | 悬挂缩进、无序号、英文标点、排序、去重、著者格式、禁止百度百科 | ~19 |

参考文献的规则最密集且相互关联（排序规则需要看所有条目、去重需要看所有条目、引用对应需要回看正文）。
因此在 Group 2 遍历时先跳过参考文献区域的深度检查，在 Group 5 中集中处理。

### Group 6: Cross-references (交叉引用) — 全局扫描

| 遍历对象 | 触发规则示例 | 规则数 |
|---------|------------|--------|
| 全文段落(第二次轻量扫描) | 图表编号与正文引用对应、参考文献列表与正文引用对应 | ~3 |

**说明**：这是唯一需要"第二次"扫描段落的 Group，但只做正则匹配收集编号/引用对，不做样式检查，开销很小。

---

# 第七部分：双擎独立校验机制 (落实 Req-6)

## 15. 双擎分工

| 引擎 | 职责 | 处理的规则类型 | 规则数 |
|------|------|--------------|--------|
| **Python (Docx_Engine)** | 所有确定性格式/正则/计数检查 | `paragraph_style`, `global_property`, `regex_match`, `count_check`, `cross_reference`, `text_match`, `forbidden_words` | ~152 |
| **Claude Sonnet 4.5 (Claude_Engine)** | 语义判断、上下文理解 | `ai_semantic` | ~12 |

## 16. Claude 引擎处理的具体规则清单

以下规则标记为 `engine: Claude` 或 `engine: Python+Claude`，**仅这些规则**调用 Claude API：

| 规则场景 | 所属区域 | Claude 任务 |
|---------|---------|------------|
| 摘要四要素完整性 | abstract_cn | 判断是否包含目的、方法、结果、结论 |
| 摘要质量评估 | abstract_cn | 是否过于空泛、是否有数据支撑 |
| 英文翻译一致性 | abstract_en | 英文摘要与中文摘要的关键术语是否对应 |
| 标点滥用语境判断 | body_chapter | Python统计频率异常后，Claude判断是否真的滥用 |
| 段落连贯性 | body_chapter | 段落是否支离破碎、逻辑断裂 |
| 句子质量 | body_chapter | 是否有病句、语法错误 |
| 口语化深度判断 | body_chapter | Python找到疑似口语后，Claude二次确认 |
| 结论深度评估 | body_chapter (末章) | 结论是否有独立见解、是否只是重复摘要 |
| 研究不足合理性 | body_chapter (末章) | "研究不足"部分是否流于形式 |
| 专有名词一致性 | 全文 | 同一术语是否全文统一（如"人工智能"vs"AI"混用） |
| 数据来源可信度 | body_chapter | 数据来源是否标注、是否可信 |
| 文献综述充实度 | body_chapter | 文献综述是否只是罗列、缺乏归纳分析 |

## 17. 独立运行机制

```python
# orchestrator.py 核心调度逻辑
import threading

def run_check(doc, zone_map, rules, api_key=None):
    # 分离规则
    python_rules = [r for r in rules if r['engine'] in ('Python', 'Python+Manual')]
    claude_rules = [r for r in rules if 'Claude' in r['engine']]
    
    python_issues = []
    claude_issues = []
    
    # Python 引擎同步执行（主线程）
    python_issues = docx_engine.run(doc, zone_map, python_rules)
    
    # Claude 引擎异步执行（子线程，可选）
    if api_key and claude_rules:
        thread = threading.Thread(
            target=lambda: claude_issues.extend(
                claude_engine.run(doc, zone_map, claude_rules, api_key)
            )
        )
        thread.start()
        thread.join(timeout=120)  # 最长等待2分钟
    
    # 合并结果
    all_issues = issue_merger.merge(python_issues, claude_issues)
    return all_issues
```

## 18. Claude 引擎实现规范

### 18.1 调用策略

- **按区域批量发送**，不按单段落发送（减少API调用次数和成本）
- 每次调用附带 system prompt 说明角色和输出格式要求
- 设置 `max_tokens=2000` 防止过长响应
- 单次调用超时 30 秒自动跳过，记录 `"Claude未响应，该规则跳过"`
- 总超时 120 秒，超时后所有未完成的 Claude 规则标记为 `"AI审查超时跳过"`

### 18.2 Claude 开关（关键设计）

**Claude 引擎为可选模块**，GUI 中提供 "启用AI辅助审查" 复选框：
- **关闭时**（默认）：所有 `engine: Claude` 的规则跳过，在报告中标注 `"该规则需要AI辅助，本次未启用，建议人工复核"`
- **开启时**：需要输入有效的 Anthropic API Key，Claude 引擎启动

这样即使没有 API Key，程序也能完整运行 Python 引擎的 ~152 条规则。

### 18.3 成本控制

一篇 2 万字论文的 Claude 调用估算：
- 摘要(中英文) ~2000 字 → 1 次调用
- 正文(按章批量) ~18000 字 → 5-6 次调用
- 总计 ~7-8 次调用，~30000 input tokens + ~5000 output tokens
- 估算成本：~$0.10-0.15 / 篇论文

---

# 第八部分：安全标注与降级方案 (落实 Req-2 & Req-7)

## 19. 红线警告

```
╔══════════════════════════════════════════════════════════════╗
║  绝对禁止使用 python-docx 操作底层 XML 插入 <w:comment>     ║
║  绝对禁止任何形式的 XML 写入操作                             ║
║  只允许使用 python-docx 的高级 API（add_run、font属性等）    ║
╚══════════════════════════════════════════════════════════════╝
```

## 20. 文件安全保障

```python
# 永远先复制，操作副本，原文件绝对不动
import shutil
from datetime import datetime

def safe_copy(input_path):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    stem = os.path.splitext(os.path.basename(input_path))[0]
    output_docx = f'{stem}_审查结果_{timestamp}.docx'
    output_txt = f'{stem}_审查报告_{timestamp}.txt'
    shutil.copy2(input_path, output_docx)
    return output_docx, output_txt
```

## 21. 三级降级标注链

### 优先方案：独立段落标注（推荐）

在违规段落的**下方**插入一个全新的段落作为标注。视觉效果最接近"旁注"。

```python
def annotate_independent_paragraph(doc, para_index, issues):
    """在 para_index 对应段落的下方插入标注段落"""
    target_para = doc.paragraphs[para_index]
    
    # 1. 对违规段落做黄色高亮
    for run in target_para.runs:
        run.font.highlight_color = WD_COLOR_INDEX.YELLOW
    
    # 2. 在下方插入新段落
    new_para = insert_paragraph_after(target_para)  # 见下方实现
    
    # 3. 合并同段落的多条 Issue
    annotation_text = "【系统审查建议】\n"
    for idx, issue in enumerate(issues, 1):
        annotation_text += f'  {idx}. [{issue.rule_id}] {issue.message}\n'
    
    # 4. 设置标注样式：红色、加粗、小五号
    run = new_para.add_run(annotation_text.strip())
    run.font.color.rgb = RGBColor(255, 0, 0)
    run.font.bold = True
    run.font.size = Pt(9)  # 小五号
    new_para.paragraph_format.space_before = Pt(2)
    new_para.paragraph_format.space_after = Pt(6)


def insert_paragraph_after(paragraph):
    """在指定段落后插入新段落（使用python-docx安全API）"""
    new_p = OxmlElement('w:p')
    paragraph._element.addnext(new_p)
    new_para = Paragraph(new_p, paragraph._parent)
    return new_para
```

### 降级方案1：段落末尾追加 Run

当无法插入独立段落时（如段落在表格单元格内），降级为在段落末尾追加 Run：

```python
def annotate_inline_suffix(para, issues):
    """降级：在段落末尾追加红色加粗文本"""
    for run in para.runs:
        run.font.highlight_color = WD_COLOR_INDEX.YELLOW
    combined = ' | '.join(f'[{i.rule_id}]{i.message}' for i in issues)
    suffix = f' 【系统审查建议：{combined}】'
    run = para.add_run(suffix)
    run.font.color.rgb = RGBColor(255, 0, 0)
    run.font.bold = True
    run.font.size = Pt(9)
```

### 降级方案2：仅记录到报告文件

如果连追加 Run 都失败（极端情况），仅记录到 TXT 审查报告，不修改文档。

### 21.1 降级决策逻辑

```python
def annotate_issue(doc, para_index, issues):
    try:
        annotate_independent_paragraph(doc, para_index, issues)
    except Exception as e1:
        logger.warning(f'独立段落标注失败({e1})，降级为末尾追加')
        try:
            annotate_inline_suffix(doc.paragraphs[para_index], issues)
        except Exception as e2:
            logger.error(f'所有标注方式失败({e2})，仅记录到报告')
            # issues 会被写入 TXT 报告
```

### 21.2 Issue 合并规则

**同一段落的多条 Issue 合并为一个标注**，避免段落被淹没：

```python
# issue_merger.py
def group_by_paragraph(issues):
    """将 Issue 列表按 paragraph_index 分组"""
    groups = defaultdict(list)
    for issue in issues:
        groups[issue.paragraph_index].append(issue)
    return groups  # {para_index: [issue1, issue2, ...]}
```

### 21.3 高亮粒度

- **段落级高亮**：标题格式错误、缩进错误等 → 整段黄色高亮
- **Run级高亮**：标点错误、禁用词等 → 仅对包含违规字符的 run 做黄色高亮
- 规则的 conditions 中可设置 `"highlight_scope": "paragraph"` 或 `"run"`

---

# 第九部分：极简 GUI (落实 Req-6)

## 22. 界面规格

```
┌──────────────────────────────────────────────────────────┐
│  北大光华 EMBA 论文格式审查工具 v1.0                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  论文文件：  [________________________] [选择文件...]     │
│  MD规则文件：[________________________] [选择文件...]     │
│                                                          │
│  检查级别：                                               │
│    ○ 仅 ★★★★★ 必须项                                    │
│    ○ ★★★★☆ 以上                                         │
│    ● 全部 164 条规则                                      │
│                                                          │
│  □ 启用 AI 辅助审查（需 Claude API Key）                  │
│  API Key：[__________________________________________]    │
│                                                          │
│  [          开 始 审 查          ]                        │
│                                                          │
│  ┌─ 审查进度 ──────────────────────────────────────────┐ │
│  │ ████████████████████░░░░░░░░ 62% (102/164)          │ │
│  │ 当前：Group 2 — 正在检查正文段落格式...              │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ 审查结果摘要 ──────────────────────────────────────┐ │
│  │  发现 47 个问题：                                    │ │
│  │    格式类: 23  │ 标点类: 8  │ 参考文献类: 12        │ │
│  │    图表类: 4   │ AI语义类: 0 (未启用)                │ │
│  │  覆盖率核对：164/164 规则已检查 ✓                    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ 运行日志（实时滚动）─────────────────────────────┐  │
│  │ [14:30:01] 加载规则库：164条规则                   │  │
│  │ [14:30:02] 覆盖率核对通过 ✓                        │  │
│  │ [14:30:03] 区域识别完成：发现10个区域               │  │
│  │ [14:30:04] Group 1 检查完成：2个问题                │  │
│  │ [14:30:08] Group 2 检查完成：31个问题               │  │
│  │ [14:30:10] Group 3 检查完成：5个问题                │  │
│  │ [14:30:11] Group 4 检查完成：3个问题                │  │
│  │ [14:30:13] Group 5 检查完成：6个问题                │  │
│  │ [14:30:14] Group 6 检查完成：0个问题                │  │
│  │ [14:30:14] Claude引擎未启用，12条语义规则跳过       │  │
│  │ [14:30:16] 标注写入完成                             │  │
│  │ [14:30:16] ✓ 审查完成！                             │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  输出文件：                                              │
│  📄 论文_审查结果_20260303_143016.docx    [打开文件]     │
│  📄 论文_审查报告_20260303_143016.txt     [打开文件]     │
└──────────────────────────────────────────────────────────┘
```

## 23. GUI 实现要点

- 使用 `tkinter.ttk` 的 `Progressbar` 组件实现进度条
- 检查过程在子线程中运行，通过 `queue.Queue` 向主线程推送进度更新，**避免UI冻结**
- 日志区使用 `ScrolledText`，自动滚动到最新行
- 审查完成后，输出文件路径可点击打开（`os.startfile` on Windows / `subprocess.run(['open', path])` on macOS）
- API Key 输入框使用 `show='*'` 隐藏显示

---

# 第十部分：技术预研与已知限制

## 24. python-docx 能力边界

Cursor 必须在编码前明确以下能力边界，避免写出无法运行的代码：

### 24.1 python-docx 可直接读取的属性

| 属性 | API |
|------|-----|
| 段落文本 | `para.text`, `run.text` |
| 段落样式 | `para.style.name` |
| 字体名称 | `run.font.name` |
| 字号 | `run.font.size` (Pt) |
| 加粗/斜体 | `run.font.bold`, `run.font.italic` |
| 对齐 | `para.paragraph_format.alignment` |
| 首行缩进 | `para.paragraph_format.first_line_indent` |
| 悬挂缩进 | 通过XML: `pPr/ind@hanging` |
| 行距 | `para.paragraph_format.line_spacing` |
| 段前段后 | `para.paragraph_format.space_before/after` |
| 页面尺寸 | `section.page_width/height` (EMU) |
| 页边距 | `section.top/bottom/left/right_margin` (EMU) |
| 表格 | `doc.tables`, `table.rows`, `cell.text` |
| 内联图 | `doc.inline_shapes` |
| 高亮色 | `run.font.highlight_color` (可写) |

### 24.2 需要 lxml 安全读取 XML 的属性（只读！）

| 属性 | XML路径 | 用于规则 |
|------|---------|---------|
| 页眉内容 | `w:hdr/w:p/w:r/w:t` | HEADER_03 (奇偶页内容) |
| 页脚/页码 | `w:ftr/w:p/w:fldSimple` | HEADER_05,06,07,08,09 |
| 脚注 | `word/footnotes.xml` | FOOT_01~07 |
| 域代码(页码格式) | `w:fldChar`, `w:instrText` | 页码罗马/阿拉伯 |
| 分节符类型 | `w:sectPr/w:type` | 页眉起始范围 |
| 奇偶页设置 | `w:settings/w:evenAndOddHeaders` | HEADER_03 |
| 中文字体(eastAsia) | `w:rPr/w:rFonts@w:eastAsia` | 所有中文字体检查 |
| 页眉下划线 | `w:pBdr/w:bottom` | HEADER_04 |

### 24.3 完全无法通过 docx 检测的属性

| 属性 | 原因 | 处理方式 |
|------|------|---------|
| 图片内部文字字号 | 图片是位图，无法解析内部文字 | 标记为 `skip`，报告中注明"需人工复核" |
| 实际渲染后的页数 | python-docx不做排版渲染 | 用字数估算（2万字约50页） |
| 目录是否由Word自动生成 | 域代码可检测，但不100%可靠 | 检测TOC域代码存在性，降级为semi |
| 图表是否"清晰" | 主观视觉判断 | 标记为 `skip` |

---

# 第十一部分：异常处理与安全保障

## 25. 异常处理策略

| 异常场景 | 处理方式 |
|---------|---------|
| docx 文件无法打开 | 弹窗提示"文件损坏或加密"，终止 |
| docx 文件有密码保护 | 弹窗提示"请先解除密码保护"，终止 |
| MD 清单文件格式异常 | 弹窗提示解析失败位置，终止 |
| 覆盖率核对失败 | 弹窗提示 + 输出 coverage_report.txt，终止 |
| 某条规则执行报错 | logger.error 记录，**跳过该规则继续检查**，不crash |
| 段落没有 font 属性 | 回退到段落样式的默认字体，如果仍无则跳过 |
| Claude API Key 无效 | 弹窗提示，Claude引擎跳过，Python引擎继续 |
| Claude API 超时(30s) | 该次调用跳过，记录到日志 |
| Claude API 总超时(120s) | 所有未完成的Claude规则跳过 |
| 标注写入失败 | 按降级链处理（独立段落→末尾追加→仅记录报告） |
| 保存docx失败 | 弹窗提示"无法保存，请检查文件是否被占用" |

## 26. 核心原则：绝不crash

```python
# 每条规则的执行都包裹在 try-except 中
for rule in active_rules:
    try:
        executor = get_executor(rule['check_type'])
        result = executor(element, rule['conditions'])
        if result:
            issues.extend(result)
    except Exception as e:
        logger.error(f'规则 {rule["rule_id"]} 执行失败: {e}')
        skipped_rules.append(rule['rule_id'])
        continue  # 绝不中断
```

---

# 第十二部分：输出规格

## 27. 输出文件

每次审查生成两个文件：

### 27.1 审查结果 docx

- 文件名：`{原文件名}_审查结果_{YYYYMMDD_HHmmss}.docx`
- 内容：原文档的副本 + 黄色高亮 + 红色标注段落
- 标注格式见第八部分

### 27.2 审查报告 txt

- 文件名：`{原文件名}_审查报告_{YYYYMMDD_HHmmss}.txt`
- 内容结构：

```
═══════════════════════════════════════════════
  北大光华 EMBA 论文格式审查报告
═══════════════════════════════════════════════
审查时间：2026-03-03 14:30:16
论文文件：张三_EMBA论文.docx
规则版本：164条 (auto:136, semi:28)
检查级别：全部
AI辅助：未启用

───────────────────────────────────────────────
  审查结果摘要
───────────────────────────────────────────────
发现问题总数：47
  ★★★★★ 级：32
  ★★★★☆ 级：11
  ★★★☆☆ 级：4
  
按类别统计：
  封面格式：3
  页面设置：1
  ...

跳过的规则：2
  FIG_04 (图中标注文字) — 无法自动检测，需人工复核
  FIGTBL_01 (图表清晰度) — 无法自动检测，需人工复核

───────────────────────────────────────────────
  详细问题清单
───────────────────────────────────────────────
[#1] 规则 COVER_01 | ★★★★★ | 区域: cover | 段落 3
     封面主标题必须为黑体一号(26pt)、加粗、居中，且不超过20个汉字。
     当前状态：字体=宋体，字号=16pt

[#2] 规则 PUNCT_01 | ★★★★★ | 区域: body_chapter | 段落 47
     中文正文中发现英文逗号","，应使用中文逗号"，"。
     位置：第23个字符
...
```

---

# 第十三部分：给 Cursor 的分步开发指令

## 28. 开发顺序

**每完成一步必须停下来与我确认，不要一次性生成所有代码。**

### Step 0: 环境准备与技术预研

1. 创建项目目录结构（按第二部分5节）
2. 创建 `requirements.txt`：`python-docx>=0.8.11`, `lxml>=4.9`, `anthropic>=0.39.0`
3. 创建 `config.py`，定义所有常量（EMU换算系数、默认路径等）
4. 创建 `utils.py`，实现：
   - `emu_to_cm(emu)` / `cm_to_emu(cm)` / `emu_to_pt(emu)` / `pt_to_emu(pt)`
   - `safe_read_xml(element, xpath)` — 安全读取XML属性的封装函数
   - `get_east_asia_font(run)` — 读取中文字体（eastAsia属性）
5. 在 `utils.py` 中列出 python-docx 无法检测的规则，标记为 SKIP_LIST

**交付物**：项目骨架 + config.py + utils.py
**验收标准**：`python -c "import docx; import lxml; print('OK')"` 通过

### Step 1: MD 解析器 + 规则库自动生成 + 覆盖率核对 (Req-3 & Req-5)

1. 阅读 MD 清单文件，理解其结构（附录A有详细的结构契约说明）
2. 实现 ：按附录A的解析算法，自动从 MD 清单中提取所有 ✅/⚠️ 规则
3. 实现 ：调用解析器，自动推断每条规则的 check_type 和 conditions，生成 
4. 运行生成器，统计推断结果：
   - Python 正则成功推断的规则数（预期 ~60-70%）
   - 推断为  的规则数（需 Claude NLP 补全或人工填写）
5. 如果有 Claude API Key，运行 NLP 辅助补全（仅此一次，不是每次审查时调用）
6. 输出需人工补全的规则清单，**暂停等待我确认**
7. 编写 ，实现 MD ↔ 规则库双向核对
8. 运行核对脚本，确认覆盖率 100%

**交付物**： +  + (自动生成) + 
**验收标准**：运行  输出覆盖率 100%

### Step 2: 人工补全 conditions + 规则库定稿

1. 审查 Step 1 输出的「需人工补全」规则清单
2. 与我一起逐条确认/修正 check_type 和 conditions
3. 将修正内容写入 （人工补丁文件）
4. 重新运行  更新 JSON
5. 再次运行覆盖率核对，确认 100%

**交付物**：定稿版  + 
**验收标准**：所有规则的 check_type 均非 unknown，所有 conditions 无  标记

### Step 3: 区域识别模块 (zone_detector.py)

1. 实现第五部分描述的 `detect_zones()` 函数
2. 用 DOC 排版模板文件测试，确认能正确识别所有区域

**交付物**：`zone_detector.py`
**验收标准**：对模板文件输出正确的 zone_map

### Step 4: 七种执行器实现 (rule_executors.py)

1. 实现 7 种 `check_type` 的执行器函数
2. 每种执行器编写至少 2 个单元测试

**交付物**：`rule_executors.py` + 测试
**验收标准**：所有单元测试通过

### Step 5: Python 引擎组装 (docx_engine.py)

1. 实现 6 个 Group 的分组遍历逻辑
2. 将遍历与执行器串联：遍历到元素 → 筛选zone匹配的规则 → 调用执行器 → 收集Issue
3. 用 test_errors.docx 测试

**交付物**：`docx_engine.py`
**验收标准**：对错误样本能检测出预期的Issue

### Step 6: Claude 引擎实现 (claude_engine.py)

1. 实现 Claude API 调用封装
2. 实现按区域批量发送逻辑
3. 实现超时处理和错误降级
4. 实现 Claude 开关（关闭时跳过所有ai_semantic规则）

**交付物**：`claude_engine.py`
**验收标准**：有API Key时能正常调用；无Key时graceful跳过

### Step 7: 安全标注模块 (safe_annotator.py)

1. 实现三级降级链
2. 实现 Issue 按段落分组合并
3. 实现高亮粒度控制（段落级 vs run级）
4. 测试：标注后的docx用Word打开不报错

**交付物**：`safe_annotator.py`
**验收标准**：标注后的docx在Microsoft Word中正常打开，无损坏警告

### Step 8: 调度器 + Issue合并 (orchestrator.py + issue_merger.py)

1. 实现主控流程：加载规则 → 核对覆盖率 → 识别区域 → 运行双擎 → 合并Issue → 标注 → 保存
2. 实现进度回调机制（供GUI使用）

**交付物**：`orchestrator.py` + `issue_merger.py`

### Step 9: GUI 整合 (gui.py + main.py)

1. 按第九部分规格实现 Tkinter 界面
2. 子线程运行检查，主线程更新UI
3. 实现进度条、日志、结果摘要、文件打开按钮

**交付物**：`gui.py` + `main.py`
**验收标准**：完整走通一遍审查流程，UI不冻结

### Step 10: 集成测试

1. 用合规模板测试 → 期望 0 个 Issue（或仅有已知的skip规则提示）
2. 用错误样本测试 → 期望触发预期的 Issue
3. 用空白 docx 测试 → 期望不crash，报告"缺少必要章节"
4. 测试 Claude 开/关两种模式
5. 测试不同检查级别（仅★★★★★ / 全部）

---

# 附录A：MD 清单自动解析与规则库生成规范

## A.1 核心设计理念

**MD 清单是系统的唯一事实标准（Single Source of Truth）。**

`rules_registry.json` **不允许手工编写**，必须由 `generate_registry.py` 自动解析 MD 清单生成。
这样做的好处：
- MD 清单更新后，重新运行生成器即可同步规则库，不存在“两边不一致”的风险
- 消除了人工转录规则时不可避免的抄错、漏抄
- 未来 MD 清单增删规则时，规则库自动跟随，零维护成本
- `verify_coverage.py` 的双向核对变成同源校验，覆盖率天然 100%

## A.2 MD 清单的结构契约

Cursor 在编写解析器之前，**必须先打开并通读 MD 清单文件**，理解其固定结构。以下是契约：

```
## {章节编号}、{章节名}              <- 一级章节标题（如 "一、封面页格式"）
### {子章节编号} {子章节名}      <- 二级章节标题（如 "11.1 图的要求"）

| 要素 | 格式要求 | 紧急程度 | 可编程性 | 检测方法说明 |    <- 表头（固定5列）
|------|----------|----------|----------|--------------|
| **{要素名}** | {格式要求文本} | {星级} | {✅/⚠️/❌} | {检测方法} |

**出处**：{来源引用}
```

关键特征：
- 每个章节由 `##` 或 `###` 标题开头，每个章节包含一个 Markdown 表格
- 表头固定 5 列：要素 | 格式要求 | 紧急程度 | 可编程性 | 检测方法说明
- `可编程性` 列决定是否纳入规则库：✅ 和 ⚠️ 纳入，❌ 排除
- `要素` 列可能被 `**` 加粗包裹，解析时需去除
- 同名要素可能出现在不同章节（如“编号规则”、“正文引用”、“行距”各 3 次），必须用 **章节名+要素名** 做复合Key
- `格式要求` 列是生成 conditions 的主要数据源（含字体、字号、对齐、行距等参数）
- `检测方法说明` 列是推断 check_type 的重要参考

## A.3 解析流程总览

```
MD清单文件
    |
    v
[md_parser.py]  -- Step A: Python正则解析MD表格
    |               提取: 章节名、要素名、格式要求、紧急程度、可编程性、检测方法
    |               过滤: 仅保留 ✅ 和 ⚠️
    v
[推断引擎]      -- Step B: 从文本中推断 check_type + conditions
    |               Python正则提取字体/字号/对齐/行距等
    |               覆盖率: 预计 60-70%
    v
[Claude NLP]    -- Step C: 可选，对unknown规则调用Claude补全
    |               仅在生成阶段调用一次，非每次审查时调用
    |               覆盖率提升至 90-95%
    v
[manual_overrides.json]  -- Step D: 人工补全兆底
    |               针对剩余 5-10% 无法自动推断的规则
    v
rules_registry.json  <- 最终产物
```

## A.4 md_parser.py 核心实现

```python
# md_parser.py
import re, json

def parse_md_to_rules(md_path: str) -> list[dict]:
    """
    解析 MD 清单，生成结构化规则列表。
    返回: list[dict]，每条规则包含 MD 原始信息 + 推断的 check_type/conditions。
    """
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    rules = []
    current_section = None
    section_counter = {}  # {prefix: int}
    
    for line in content.split("\n"):
        stripped = line.strip()
        
        # 1. 识别章节标题
        if stripped.startswith("## ") and not_meta_line(stripped):
            current_section = stripped.lstrip("#").strip()
            continue
        if stripped.startswith("### ") and is_sub_section(stripped):
            current_section = stripped.lstrip("#").strip()
            continue
        
        # 2. 跳过非表格行、表头行、分隔线
        if not stripped.startswith("|") or stripped.startswith("|---"):
            continue
        if "要素" in stripped[:15]:  # 表头行
            continue
        
        # 3. 解析表格列
        cells = [c.strip() for c in stripped.split("|") if c.strip()]
        if len(cells) < 4: continue
        
        element_name = cells[0].replace("**", "")  # 去加粗
        format_requirement = cells[1]
        urgency = cells[2].strip()
        programmability = cells[3].strip()
        detection_method = cells[4] if len(cells) > 4 else ""
        
        # 4. 仅保留 ✅ 和 ⚠️
        is_auto = "\u2705" in programmability
        is_semi = "\u26a0" in programmability
        if not is_auto and not is_semi: continue
        automation_level = "auto" if is_auto else "semi"
        
        # 5. 生成 rule_id
        prefix = section_to_prefix(current_section)
        section_counter[prefix] = section_counter.get(prefix, 0) + 1
        rule_id = f"{prefix}_{section_counter[prefix]:02d}"
        
        # 6. 推断各属性
        group = infer_group(prefix, detection_method)
        zones = infer_zones(current_section)
        check_type, conditions = infer_check_type(format_requirement, detection_method, element_name)
        engine = infer_engine(automation_level, check_type, element_name)
        
        rules.append({
            "rule_id": rule_id,
            "md_source_key": f"{current_section}::{element_name}",
            "element_name": element_name,
            "format_requirement": format_requirement,  # 保留原文，方便调试
            "automation_level": automation_level,
            "urgency": urgency,
            "target_group": group,
            "target_zone": zones,
            "engine": engine,
            "check_type": check_type,
            "conditions": conditions,
            "detection_method": detection_method,
            "error_message": f"{element_name}格式不符：{format_requirement[:80]}",
            "enabled": True,
        })
    
    return rules


def not_meta_line(line):
    return "附：" not in line and "可编程" not in line


def is_sub_section(line):
    keywords = ["图的要求","表的要求","通用图表","正文引用格式",
               "文末参考文献","四种文献","论文题目要求","文字表达"]
    return any(kw in line for kw in keywords)
```

## A.5 section_to_prefix 映射规则

```python
PREFIX_MAP = {
    "封面": "COVER", "版权声明": "DECL", "页面设置": "PAGE",
    "页眉页码": "HEADER", "标点符号": "PUNCT",
    "摘要格式": "ABSTRACT_CN", "英文摘要": "ABSTRACT_EN",
    "目录": "TOC", "正文标题": "HEADING", "正文段落": "BODY",
    "图的要求": "FIG", "表的要求": "TBL", "通用图表": "FIGTBL",
    "表达式": "EXPR", "公式": "EXPR", "脚注": "FOOT",
    "正文引用格式": "REF_CITE", "文末参考文献": "REF_LIST",
    "四种文献": "REF_TYPE", "附录": "APPENDIX", "致谢": "ACK",
    "论文题目要求": "TITLE_REQ", "文字表达": "TEXT_NORM",
    "案例写作": "CASE_WRITE", "文献综述": "LIT_REVIEW",
    "案例分析": "CONCLUSION", "研究结论": "CONCLUSION",
}

def section_to_prefix(section_title):
    for keyword, prefix in PREFIX_MAP.items():
        if keyword in section_title:
            return prefix
    return "MISC"
```

## A.6 infer_group 推断规则

```python
GROUP_INFERENCE = {
    "PAGE": "Group1_Global", "HEADER": "Group1_HeaderFooter",
    "FOOT": "Group4_Footnotes",
    "REF_LIST": "Group5_References", "REF_TYPE": "Group5_References",
    "FIG": "Group3_Figures", "TBL": "Group3_Tables", "FIGTBL": "Group3_Tables",
}

def infer_group(prefix, detection_method):
    if prefix in GROUP_INFERENCE: return GROUP_INFERENCE[prefix]
    if "对应" in detection_method or "一一" in detection_method: return "Group6_CrossRef"
    return "Group2_Paragraphs"
```

## A.7 infer_check_type 推断规则（最关键）

从「格式要求」和「检测方法说明」两列文本中推断 check_type：

```python
def infer_check_type(format_req, detection_method, element_name):
    """
    返回 (check_type, conditions_skeleton)
    优先级：text_match > regex > count > forbidden > cross_ref > global > style > unknown
    """
    dm = detection_method
    fr = format_req
    
    # 1. 文本精确匹配（关键词：固定格式、请勿修改）
    if any(kw in fr for kw in ["固定格式", "请勿做任何修改"]):
        return "text_match", {"match_mode": "exact"}
    if "精确匹配" in dm or "文本匹配" in dm:
        return "text_match", {"match_mode": "contains"}
    
    # 2. 正则匹配（关键词：正则、Unicode、编号）
    if "正则" in dm or "Unicode" in dm or "编号" in element_name:
        return "regex_match", {"match_mode": "must_match"}
    
    # 3. 计数/统计（关键词：字数、不超过N个）
    if re.search(r"(不超过|不少于|至少|最多|最少)\s*\d+", fr) or "字数" in dm:
        return "count_check", parse_count_conditions(fr)
    
    # 4. 禁用词（关键词：禁止引用、不得）
    if any(kw in fr for kw in ["禁止引用", "禁止使用", "不得"]) or "禁用词" in dm:
        return "forbidden_words", {"match_mode": "any"}
    
    # 5. 交叉引用（关键词：对应、一一）
    if "对应" in dm or "引用匹配" in dm or "一一" in fr:
        return "cross_reference", {"must_match": True}
    
    # 6. 全局属性（关键词：A4、页边距、cm）
    if any(kw in fr for kw in ["A4", "页边距", "cm", "纸张", "距边界"]):
        return "global_property", parse_global_conditions(fr)
    
    # 7. 段落样式（含字体、字号、对齐等）
    style_kw = ["字体","字号","号","宋体","黑体","仿宋","Times",
                "居中","对齐","缩进","行距","段前","段后","加粗","倍行距"]
    if any(kw in fr for kw in style_kw):
        return "paragraph_style", parse_style_conditions(fr)
    
    # 8. 无法推断
    return "unknown", {"_needs_manual_review": True, "_raw_requirement": fr}
```

## A.8 parse_style_conditions — 从文本自动提取样式参数

```python
FONT_SIZE_MAP = {
    "一号": 26, "小一": 24, "二号": 22, "小二": 18,
    "三号": 16, "小三": 15, "四号": 14, "小四": 12,
    "五号": 10.5, "小五": 9
}

def parse_style_conditions(format_req):
    cond = {}
    fr = format_req
    
    # 字体
    for cn, val in {"黑体":"黑体","宋体":"宋体","仿宋":"仿宋","楷体":"楷体"}.items():
        if cn in fr: cond["font_name_cn"] = val; break
    if "Times New Roman" in fr or "Times" in fr:
        cond["font_name_en"] = "Times New Roman"
    
    # 字号
    for cn_size, pt in FONT_SIZE_MAP.items():
        if cn_size in fr: cond["font_size_pt"] = pt; break
    
    # 对齐
    if "居中" in fr: cond["alignment"] = "CENTER"
    elif "两端对齐" in fr: cond["alignment"] = "JUSTIFY"
    elif "左对齐" in fr: cond["alignment"] = "LEFT"
    
    if "加粗" in fr: cond["bold"] = True
    
    # 行距
    m = re.search(r"(\d+\.?\d*)\s*倍行距", fr)
    if m: cond["line_spacing_type"] = "MULTIPLE"; cond["line_spacing_value"] = float(m.group(1))
    m2 = re.search(r"行距[:：]?\s*(\d+)\s*磅", fr)
    if m2: cond["line_spacing_type"] = "EXACTLY"; cond["line_spacing_value_pt"] = int(m2.group(1))
    
    # 缩进
    m3 = re.search(r"首行缩进\s*(\d+\.?\d*)\s*字符", fr)
    if m3: cond["first_line_indent_char"] = float(m3.group(1))
    m4 = re.search(r"悬挂缩进\s*(\d+\.?\d*)\s*字符", fr)
    if m4: cond["hanging_indent_char"] = float(m4.group(1))
    
    # 段前段后
    m5 = re.search(r"段前\s*(\d+)\s*磅", fr)
    if m5: cond["space_before_pt"] = int(m5.group(1))
    m6 = re.search(r"段后\s*(\d+)\s*磅", fr)
    if m6: cond["space_after_pt"] = int(m6.group(1))
    
    return cond


def parse_global_conditions(format_req):
    cond = {}
    mm = re.findall(r"(\d+)\s*[x×]\s*(\d+)\s*mm", format_req)
    if mm:
        cond["page_width_cm"] = int(mm[0][0]) / 10
        cond["page_height_cm"] = int(mm[0][1]) / 10
    for label, key in [("上","top_margin_cm"),("下","bottom_margin_cm"),
                       ("左","left_margin_cm"),("右","right_margin_cm")]:
        m = re.search(label + r"\s*(\d+\.?\d*)\s*cm", format_req)
        if m: cond[key] = float(m.group(1))
    return cond


def parse_count_conditions(format_req):
    cond = {}
    m = re.search(r"不超过\s*(\d+)", format_req)
    if m: cond["max_value"] = int(m.group(1))
    m2 = re.search(r"(不少于|至少)\s*(\d+)", format_req)
    if m2: cond["min_value"] = int(m2.group(2))
    if "字" in format_req: cond["count_type"] = "chinese_chars"
    elif "条" in format_req or "篇" in format_req: cond["count_type"] = "items"
    return cond
```

## A.9 infer_engine 推断规则

```python
CLAUDE_KEYWORDS = ["标点滥用", "翻译一致性", "段落长度", "句子长度",
    "图表清晰度", "禁止病句错字", "统一性", "专有名词",
    "数据来源", "讨论深度", "研究不足", "禁止滥用标点", "文献综述"]

def infer_engine(automation_level, check_type, element_name):
    if check_type == "ai_semantic": return "Claude"
    if any(kw in element_name for kw in CLAUDE_KEYWORDS): return "Python+Claude"
    if automation_level == "semi": return "Python+Manual"
    return "Python"
```

## A.10 Claude NLP 辅助补全 conditions（可选步骤）

纯 Python 正则只能提取 60-70% 的 conditions。对于 `check_type=unknown` 的规则，
可调用 Claude Sonnet 4.5 进行 NLP 辅助解析：

```python
def enhance_conditions_with_claude(rules, api_key):
    """
    对 check_type=unknown 的规则调用 Claude 补全。
    仅在规则库生成阶段调用一次，不在每次审查论文时调用。
    """
    incomplete = [r for r in rules
                  if r["check_type"] == "unknown"
                  or r["conditions"].get("_needs_manual_review")]
    
    if not incomplete or not api_key: return rules
    
    prompt = "\n".join([
        f"Rule {r['rule_id']}: element={r['element_name']}, "
        f"requirement={r['format_requirement']}, "
        f"detection={r['detection_method']}"
        for r in incomplete
    ])
    
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4000,
        system="""You are a python-docx format checking expert.
For each rule, infer check_type (one of: paragraph_style / global_property / 
regex_match / count_check / cross_reference / text_match / forbidden_words / 
ai_semantic) and conditions (JSON). Output ONLY a JSON array.""",
        messages=[{"role": "user", "content": prompt}]
    )
    
    enhanced = json.loads(response.content[0].text)
    emap = {e["rule_id"]: e for e in enhanced}
    for rule in incomplete:
        if rule["rule_id"] in emap:
            e = emap[rule["rule_id"]]
            rule["check_type"] = e.get("check_type", rule["check_type"])
            rule["conditions"] = e.get("conditions", rule["conditions"])
    return rules
```

## A.11 generate_registry.py 入口

```python
# generate_registry.py
import json, os
from md_parser import parse_md_to_rules, enhance_conditions_with_claude

def main():
    md_path = "EMBA论文格式排版要求清单_补充完善版.md"
    output_path = "rules_registry.json"
    overrides_path = "manual_overrides.json"
    
    api_key = input("Claude API Key（回车跳过NLP补全）：").strip() or None
    
    # Step A: Python 解析
    rules = parse_md_to_rules(md_path)
    print(f"从 MD 中解析出 {len(rules)} 条可编程规则")
    
    known = [r for r in rules if r["check_type"] != "unknown"]
    unknown = [r for r in rules if r["check_type"] == "unknown"]
    print(f"  Python 推断成功: {len(known)} 条")
    print(f"  需 NLP/人工: {len(unknown)} 条")
    
    # Step B: Claude NLP（可选）
    if unknown and api_key:
        print("正在调用 Claude NLP...")
        rules = enhance_conditions_with_claude(rules, api_key)
        still_unknown = [r for r in rules if r["check_type"] == "unknown"]
        print(f"  Claude 补全后仍未知: {len(still_unknown)} 条")
    
    # Step C: 应用人工补丁
    if os.path.exists(overrides_path):
        with open(overrides_path, "r", encoding="utf-8") as f:
            overrides = json.load(f)
        ov_map = {o["rule_id"]: o for o in overrides}
        for rule in rules:
            if rule["rule_id"] in ov_map:
                ov = ov_map[rule["rule_id"]]
                rule["check_type"] = ov.get("check_type", rule["check_type"])
                rule["conditions"] = ov.get("conditions", rule["conditions"])
                rule["conditions"].pop("_needs_manual_review", None)
        print(f"  应用了 {len(ov_map)} 条人工补丁")
    
    # Step D: 写入 JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)
    print(f"\n规则库已生成：{output_path}")
    
    # Step E: 报告未完成项
    remaining = [r for r in rules if r["check_type"] == "unknown"
                 or r["conditions"].get("_needs_manual_review")]
    if remaining:
        print(f"\n⚠️ 以下 {len(remaining)} 条规则仍需人工补全：")
        for r in remaining:
            print(f"  {r['rule_id']}: {r['element_name']}")
    else:
        print("\n✓ 所有规则已完成！")

if __name__ == "__main__":
    main()
```

## A.12 manual_overrides.json 格式

当 Python + Claude NLP 仍无法推断的规则，由人工编写补丁：

```json
[
  {
    "rule_id": "HEADER_03",
    "check_type": "paragraph_style",
    "conditions": {
      "font_name_cn": "宋体",
      "font_size_pt": 10.5,
      "alignment": "CENTER",
      "_comment": "页眉奇偶页内容不同，需lxml读取XML检查"
    }
  }
]
```

此文件随项目版本管理，仅在少量特殊规则上使用。

---

# 附录B：Issue 数据结构

```python
@dataclass
class Issue:
    rule_id: str              # 如 'COVER_01'
    paragraph_index: int      # 段落在 doc.paragraphs 中的索引
    zone: str                 # 如 'cover', 'body_chapter'
    engine: str               # 'Python' 或 'Claude'
    urgency: str              # '★★★★★'
    message: str              # 中文提示信息
    current_value: str = ''   # 当前实际值（如 '字体=宋体'）
    highlight_scope: str = 'paragraph'  # 'paragraph' 或 'run'
    run_indices: list = None  # highlight_scope='run'时，违规run的索引列表
```

---

# 附录C：词库文件规格

### forbidden_words.txt
```
百度百科
baike.baidu.com
百度知道
zhidao.baidu.com
知乎
CSDN
```

### colloquial_words.txt
```
我认为
我觉得
众所周知
大家都知道
不言而喻
显而易见
毋庸置疑
其实
当然了
说白了
比如说
```

### research_directions.txt（27个指定研究方向）
```
人力资源管理
产业经济
战略管理
创新
创业
大数据
企业管理
公司治理
供应链管理
企业文化
企业社会责任
财务管理
广告
促销
劳动经济
审计
资本市场
组织行为
谈判
投资学
运营管理
商务统计
商业模式
企业经济学
商业经济学
管理经济学
决策
```

---

# 附录D：关键单位换算参考

```python
# python-docx 使用 EMU (English Metric Units)
# 1 inch = 914400 EMU
# 1 cm = 360000 EMU
# 1 pt = 12700 EMU
# 1 号字 = 26pt, 二号 = 22pt, 三号 = 16pt, 四号 = 14pt, 小四 = 12pt, 五号 = 10.5pt, 小五 = 9pt

EMU_PER_CM = 360000
EMU_PER_PT = 12700
EMU_PER_INCH = 914400

FONT_SIZE_MAP = {
    '一号': 26, '小一': 24, '二号': 22, '小二': 18,
    '三号': 16, '小三': 15, '四号': 14, '小四': 12,
    '五号': 10.5, '小五': 9, '六号': 7.5, '小六': 6.5,
}
```

---

> **文档结束。Cursor 请严格按照 Step 0 → Step 10 的顺序执行，每步完成后等待确认。**