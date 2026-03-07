# -*- coding: utf-8 -*-
import json

with open('D:/Projects/ThesisFormatCheck/emba_checker/manual_overrides.json', 'r', encoding='utf-8') as f:
    overrides = json.load(f)

# 6个特殊规则的修复
# 这些需要表格/脚注支持，暂时用简化版实现
fixes = [
    # MISC_13: 表中单位
    {
        "rule_id": "MISC_13",
        "check_type": "regex_match",
        "target_zone": ["body_chapter"],
        "conditions": {
            "pattern": r"单位[：:]",
            "match_mode": "must_match",
            "_comment": "表中标明量和单位"
        }
    },
    # MISC_20: 表中数字小数位
    {
        "rule_id": "MISC_20",
        "check_type": "regex_match",
        "target_zone": ["body_chapter"],
        "conditions": {
            "pattern": r"\d+\.\d+",
            "match_mode": "find_all_violations",
            "_comment": "表中数字统一小数位(简化版)"
        }
    },
    # MISC_21: 表格不跨页
    {
        "rule_id": "MISC_21",
        "check_type": "skip",
        "target_zone": ["body_chapter"],
        "conditions": {},
        "_comment": "表格跨页检测需要复杂XML处理，暂跳过"
    },
    # FOOT_05: 脚注行距
    {
        "rule_id": "FOOT_05",
        "check_type": "paragraph_style",
        "target_zone": ["body_chapter"],  # 脚注区域
        "conditions": {
            "line_spacing_type": "MULTIPLE",
            "line_spacing_value": 1.0,
            "space_before_pt": 0,
            "space_after_pt": 0,
            "_comment": "脚注: 单倍行距，段前段后0磅"
        }
    },
    # FOOT_06: 脚注编号格式
    {
        "rule_id": "FOOT_06",
        "check_type": "skip",
        "target_zone": ["body_chapter"],
        "conditions": {},
        "_comment": "脚注编号格式需要XML处理，暂跳过"
    },
    # FOOT_07: 脚注网址
    {
        "rule_id": "FOOT_07",
        "check_type": "regex_match",
        "target_zone": ["body_chapter"],
        "conditions": {
            "pattern": r"https?://|www\.",
            "match_mode": "find_all_violations",
            "_comment": "网址应在脚注标注(简化版)"
        }
    },
]

# 应用修复
for fix in fixes:
    rule_id = fix["rule_id"]
    for i, o in enumerate(overrides):
        if o["rule_id"] == rule_id:
            overrides[i] = fix
            print(f"已更新: {rule_id}")
            break
    else:
        overrides.append(fix)
        print(f"已添加: {rule_id}")

with open('D:/Projects/ThesisFormatCheck/emba_checker/manual_overrides.json', 'w', encoding='utf-8') as f:
    json.dump(overrides, f, ensure_ascii=False, indent=2)

print(f"\n共处理 {len(fixes)} 条特殊规则")
