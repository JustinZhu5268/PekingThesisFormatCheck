# 规则系统修复逻辑不一致问题

## 问题描述

当前 EMBA 论文格式检查工具的规则系统存在**修复逻辑不一致**的问题：

### 两类规则的差异

| 类型 | 示例规则 | 检查方式 | 修复方式 |
|------|----------|----------|----------|
| **样式类规则** | FONT_01, SIZE_01, ALIGN_01 等 | `conditions` 定义期望值 | 代码从 `conditions` 读取期望值并自动修复 |
| **正则类规则** | HEADING_01, FIG_NUM_01, REF_LIST_01 | `conditions.pattern` 定义检查模式 | **硬编码**在 `docx_autofixer.py` 中 |

---

## 当前实现

### 样式类规则（自动修复）

**规则定义** (`rules_registry.json`):
```json
{
  "rule_id": "FONT_01",
  "check_type": "paragraph_style",
  "element_name": "中文正文",
  "conditions": {
    "font_name_cn": "宋体",
    "font_size_pt": 10.5,
    "line_spacing": 1.5
  }
}
```

**代码实现** (`docx_autofixer.py`):
```python
def _fix_zone_paragraphs(self, zone: str, rules: List[Dict]):
    # 从 conditions 读取期望值
    for rule in rules:
        conditions = rule.get("conditions", {})
        for key, value in conditions.items():
            merged_conditions[key] = value
    
    # 应用修复
    for para in self.doc.paragraphs:
        needs_fix = self._check_needs_fix(para, merged_conditions)
        if needs_fix:
            self._apply_fix(para, merged_conditions, ...)
```

---

### 正则类规则（硬编码修复）

**规则定义** (`rules_registry.json`):
```json
{
  "rule_id": "HEADING_01",
  "check_type": "regex_match",
  "element_name": "节标题小数点",
  "conditions": {
    "pattern": "\\d+\\.\\d+\\.",
    "match_mode": "must_not_match"
  }
  // ❌ 没有修复逻辑！
}
```

**代码实现** (`docx_autofixer.py`):
```python
def _fix_heading_format(self):
    """修复节标题格式 - 硬编码"""
    # 1.1. → 1.1
    text = re.sub(r'(\d+\.\d+)\.\s+', r'\1 ', text)
    
    # 移除 "第二章 1.1" 前缀
    text = re.sub(r'第[一二三四五六七八九十]+章\s+', '', text)
```

---

## 受影响的规则

以下规则虽然已在 `rules_registry.json` 中定义，但**只有检查逻辑，没有自动修复**：

| 规则ID | 问题描述 | 当前修复方式 |
|--------|----------|--------------|
| HEADING_01 | 节标题多余小数点 (1.1.) | 硬编码 `_fix_heading_format()` |
| HEADING_02 | 章节前缀问题 (第二章 1.1) | 硬编码 `_fix_heading_format()` |
| FIG_NUM_01 | 图表编号格式 (3-1 → 3.1) | 硬编码 `_fix_figure_numbering()` |
| REF_LIST_01 | 参考文献数字序号 [1] | 硬编码 `_fix_reference_format()` |
| REF_LIST_03 | 参考文献标点混用 | 硬编码 `_fix_reference_format()` |

---

## 理想架构

### 方案：在 rules 中添加 `fix_logic` 字段

```json
{
  "rule_id": "HEADING_01",
  "check_type": "regex_replace",
  "element_name": "节标题小数点",
  "conditions": {
    "pattern": "\\d+\\.\\d+\\."
  },
  "fix_logic": {
    "type": "regex_replace",
    "find": "(\\d+\\.\\d+)\\.\\s+",
    "replace": "\\1 "
  }
}
```

### 代码修改

1. **修改 `docx_autofixer.py`**:
   - 增强 `apply_rule()` 方法，支持 `fix_logic`
   - 移除硬编码的 `_fix_heading_format()`, `_fix_figure_numbering()`, `_fix_reference_format()`

2. **统一修复入口**:
   ```python
   def fix_all(self):
       # 样式类规则（从 conditions 修复）
       self._fix_paragraph_styles()
       
       # 正则类规则（从 fix_logic 修复）
       self._fix_regex_rules()
   ```

---

## 修复步骤

### 阶段1：扩展规则引擎

- [ ] 在 `rules_registry.json` 添加 `fix_logic` 字段规范
- [ ] 在 `DocxAutoFixer` 类中添加 `_fix_regex_rules()` 方法
- [ ] 修改 `apply_rule()` 支持正则替换修复

### 阶段2：迁移现有规则

- [ ] 将 HEADING_01/02 的修复逻辑迁移到 rules
- [ ] 将 FIG_NUM_01 的修复逻辑迁移到 rules  
- [ ] 将 REF_LIST_01/03 的修复逻辑迁移到 rules

### 阶段3：清理

- [ ] 移除硬编码的 `_fix_heading_format()`
- [ ] 移除硬编码的 `_fix_figure_numbering()`
- [ ] 移除硬编码的 `_fix_reference_format()`

---

## 备注

- **检查模式** (`--check`)：两类规则都能正常检查，不受影响
- **修复模式** (`--fix`)：
  - 样式类规则 ✅ 正常工作
  - 正则类规则 ⚠️ 依赖硬编码实现

此问题待后续重构解决。

---

*创建时间: 2026-03-07*
