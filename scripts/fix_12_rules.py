# -*- coding: utf-8 -*-
import json

with open('D:/Projects/ThesisFormatCheck/emba_checker/manual_overrides.json', 'r', encoding='utf-8') as f:
    overrides = json.load(f)

# 12个可实现规则的修复
fixes = [
    # TOC_05: 目录缩进级别检测
    {
        "rule_id": "TOC_05",
        "check_type": "regex_match",
        "target_zone": ["toc"],
        "conditions": {
            "pattern": r"^\s+",
            "match_mode": "must_match",
            "_comment": "目录缩进检测"
        }
    },
    # HEADING_02: 二级标题格式
    {
        "rule_id": "HEADING_02",
        "check_type": "paragraph_style",
        "target_zone": ["body_chapter"],
        "conditions": {
            "font_size_pt": 14,
            "bold": True,
            "alignment": "LEFT",
            "line_spacing_type": "MULTIPLE",
            "line_spacing_value": 1.5,
            "space_before_pt": 24,
            "space_after_pt": 6,
            "_comment": "二级标题: 黑体四号居左, 1.5倍行距, 段前24磅段后6磅"
        }
    },
    # BODY_06: 特殊符号检测
    {
        "rule_id": "BODY_06",
        "check_type": "regex_match",
        "target_zone": ["body_chapter"],
        "conditions": {
            "pattern": r"[√●▶▲▼◆■★☆]",
            "match_mode": "must_not_match",
            "_comment": "禁止PPT符号"
        }
    },
    # MISC_01: 图编号格式
    {
        "rule_id": "MISC_01",
        "check_type": "regex_match",
        "target_zone": ["body_chapter"],
        "conditions": {
            "pattern": r"图\s*\d+\.\d+",
            "match_mode": "must_match",
            "_comment": "图编号: 2.1 格式"
        }
    },
    # MISC_09: 表编号格式
    {
        "rule_id": "MISC_09",
        "check_type": "regex_match",
        "target_zone": ["body_chapter"],
        "conditions": {
            "pattern": r"表\s*\d+\.\d+",
            "match_mode": "must_match",
            "_comment": "表编号: 2.1 格式"
        }
    },
    # EXPR_01: 公式编号格式
    {
        "rule_id": "EXPR_01",
        "check_type": "regex_match",
        "target_zone": ["body_chapter"],
        "conditions": {
            "pattern": r"式\s*\(\d+\.\d+\)",
            "match_mode": "must_match",
            "_comment": "公式编号: 式(2.1)"
        }
    },
    # EXPR_03: 公式行距
    {
        "rule_id": "EXPR_03",
        "check_type": "paragraph_style",
        "target_zone": ["body_chapter"],
        "conditions": {
            "line_spacing_type": "MULTIPLE",
            "line_spacing_value": 1.0,
            "space_before_pt": 6,
            "space_after_pt": 6,
            "_comment": "公式行距: 单倍, 段前段后6磅"
        }
    },
    # EXPR_04: 公式段落行距
    {
        "rule_id": "EXPR_04",
        "check_type": "paragraph_style",
        "target_zone": ["body_chapter"],
        "conditions": {
            "line_spacing_type": "MULTIPLE",
            "line_spacing_value": 1.0,
            "space_before_pt": 3,
            "space_after_pt": 3,
            "_comment": "公式段落: 单倍行距, 段前段后3磅"
        }
    },
    # EXPR_05: 乘号检测
    {
        "rule_id": "EXPR_05",
        "check_type": "regex_match",
        "target_zone": ["body_chapter"],
        "conditions": {
            "pattern": r"\*",
            "match_mode": "must_not_match",
            "_comment": "使用×而非*"
        }
    },
    # APPENDIX_02: 附录编号
    {
        "rule_id": "APPENDIX_02",
        "check_type": "regex_match",
        "target_zone": ["appendix"],
        "conditions": {
            "pattern": r"附录\s*[A-Z]",
            "match_mode": "must_match",
            "_comment": "附录编号: 附录A"
        }
    },
    # APPENDIX_03: 附录序号间距
    {
        "rule_id": "APPENDIX_03",
        "check_type": "paragraph_style",
        "target_zone": ["appendix"],
        "conditions": {
            "space_after_pt": 0,
            "_comment": "附录序号与标题之间空1汉字符"
        }
    },
    # TEXT_NORM_10: XX公司检测
    {
        "rule_id": "TEXT_NORM_10",
        "check_type": "regex_match",
        "target_zone": ["body_chapter"],
        "conditions": {
            "pattern": r"(XX|某某)\s*公司",
            "match_mode": "must_not_match",
            "_comment": "禁止XX公司"
        }
    },
]

# 应用修复
for fix in fixes:
    rule_id = fix["rule_id"]
    # 找到并更新
    for i, o in enumerate(overrides):
        if o["rule_id"] == rule_id:
            overrides[i] = fix
            print(f"已更新: {rule_id}")
            break
    else:
        overrides.append(fix)
        print(f"已添加: {rule_id}")

# 保持skip的2个规则: TEXT_NORM_08, CONCLUSION_05

with open('D:/Projects/ThesisFormatCheck/emba_checker/manual_overrides.json', 'w', encoding='utf-8') as f:
    json.dump(overrides, f, ensure_ascii=False, indent=2)

print(f"\n共修复 {len(fixes)} 条规则")
