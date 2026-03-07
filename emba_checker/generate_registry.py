# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 规则库生成器
从 MD 清单自动生成 rules_registry.json
"""

import json
import os
import sys
from typing import List, Dict, Optional

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from emba_checker.md_parser import parse_md_to_rules
except ImportError:
    from md_parser import parse_md_to_rules


def load_manual_overrides(overrides_path: str = None) -> Dict[str, Dict]:
    """加载人工补丁文件"""
    if overrides_path is None:
        overrides_path = os.path.join(
            os.path.dirname(__file__), 
            "manual_overrides.json"
        )
    
    if not os.path.exists(overrides_path):
        return {}
    
    try:
        with open(overrides_path, 'r', encoding='utf-8') as f:
            overrides = json.load(f)
        
        # 转换为 dict: {rule_id: override}
        return {o["rule_id"]: o for o in overrides}
    except Exception as e:
        print(f"警告：加载人工补丁失败: {e}")
        return {}


def apply_manual_overrides(rules: List[Dict], overrides: Dict[str, Dict]) -> List[Dict]:
    """应用人工补丁"""
    existing_ids = {r.get("rule_id") for r in rules}
    
    for rule in rules:
        rule_id = rule.get("rule_id")
        if rule_id in overrides:
            override = overrides[rule_id]
            
            # 更新 check_type
            if "check_type" in override:
                rule["check_type"] = override["check_type"]
            
            # 更新 conditions
            if "conditions" in override:
                rule["conditions"].update(override["conditions"])
                # 移除需要人工审核标记
                rule["conditions"].pop("_needs_manual_review", None)
                rule["conditions"].pop("_raw_requirement", None)
            
            # 更新 target_zone
            if "target_zone" in override:
                rule["target_zone"] = override["target_zone"]
            
            # 添加 error_message
            if "error_message" in override:
                rule["error_message"] = override["error_message"]
            
            # 添加注释
            if "_comment" in override:
                rule["_comment"] = override["_comment"]
            
            print(f"  应用补丁: {rule_id}")
    
    # 添加新规则（不在原始MD中的人工添加规则）
    for rule_id, override in overrides.items():
        if rule_id not in existing_ids:
            # 这是一个新添加的规则
            new_rule = {
                "rule_id": rule_id,
                "md_source": override.get("md_source", "人工添加"),
                "md_source_key": override.get("md_source_key", f"人工添加::{rule_id}"),
                "element_name": override.get("element_name", rule_id),
                "format_requirement": override.get("format_requirement", ""),
                "automation_level": override.get("automation_level", "auto"),
                "urgency": override.get("urgency", "★★★★★"),
                "target_group": override.get("target_group", "Group2_Paragraphs"),
                "target_zone": override.get("target_zone", []),
                "engine": override.get("engine", "Python"),
                "check_type": override.get("check_type", "regex_match"),
                "conditions": override.get("conditions", {}),
                "detection_method": override.get("detection_method", "人工添加"),
                "error_message": override.get("error_message", f"{rule_id} 格式不符"),
                "enabled": override.get("enabled", True),
            }
            if "_comment" in override:
                new_rule["_comment"] = override["_comment"]
            rules.append(new_rule)
            print(f"  添加新规则: {rule_id}")
    
    return rules


def generate_registry(
    md_path: str,
    output_path: str = None,
    overrides_path: str = None,
    api_key: str = None
) -> Dict[str, int]:
    """
    生成规则库
    
    Args:
        md_path: MD 清单路径
        output_path: 输出 JSON 路径
        overrides_path: 人工补丁文件路径
        api_key: Claude API Key (可选)
        
    Returns:
        统计信息 dict
    """
    if output_path is None:
        output_path = os.path.join(
            os.path.dirname(__file__),
            "rules_registry.json"
        )
    
    # Step A: Python 解析
    print("=" * 60)
    print("Step A: 解析 MD 清单...")
    rules = parse_md_to_rules(md_path)
    print(f"从 MD 中解析出 {len(rules)} 条可编程规则")
    
    # 统计
    known = [r for r in rules if r.get("check_type") != "unknown"]
    unknown = [r for r in rules if r.get("check_type") == "unknown"]
    
    print(f"  Python 推断成功: {len(known)} 条")
    print(f"  需人工/NLP: {len(unknown)} 条")
    
    # Step B: Claude NLP 补全 (可选)
    if unknown and api_key:
        print("\n" + "=" * 60)
        print("Step B: 调用 Claude NLP 补全...")
        rules = enhance_conditions_with_claude(rules, api_key)
        
        known = [r for r in rules if r.get("check_type") != "unknown"]
        unknown = [r for r in rules if r.get("check_type") == "unknown"]
        
        print(f"  Claude 补全后: {len(known)} 条")
        print(f"  仍需人工: {len(unknown)} 条")
    
    # Step C: 应用人工补丁
    print("\n" + "=" * 60)
    print("Step C: 应用人工补丁...")
    overrides = load_manual_overrides(overrides_path)
    if overrides:
        rules = apply_manual_overrides(rules, overrides)
        print(f"  应用了 {len(overrides)} 条补丁")
    else:
        print("  无人工补丁文件")
    
    # 最终统计
    auto_rules = [r for r in rules if r.get("automation_level") == "auto"]
    semi_rules = [r for r in rules if r.get("automation_level") == "semi"]
    python_rules = [r for r in rules if "Python" in r.get("engine", "")]
    claude_rules = [r for r in rules if "Claude" in r.get("engine", "")]
    
    # Step D: 写入 JSON
    print("\n" + "=" * 60)
    print("Step D: 写入规则库...")
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)
    
    print(f"规则库已生成: {output_path}")
    print(f"  总规则数: {len(rules)}")
    print(f"  全自动: {len(auto_rules)}")
    print(f"  半自动: {len(semi_rules)}")
    print(f"  Python 引擎: {len(python_rules)}")
    print(f"  Claude 引擎: {len(claude_rules)}")
    
    # Step E: 报告未完成项
    remaining = [
        r for r in rules 
        if r.get("check_type") == "unknown"
        or r.get("conditions", {}).get("_needs_manual_review")
    ]
    
    if remaining:
        print("\n" + "=" * 60)
        print(f"⚠️ 以下 {len(remaining)} 条规则仍需人工补全：")
        for r in remaining:
            print(f"  {r['rule_id']}: {r['element_name']}")
            print(f"    原始要求: {r.get('format_requirement', '')[:60]}...")
    else:
        print("\n" + "=" * 60)
        print("✓ 所有规则已完成！")
    
    return {
        "total": len(rules),
        "auto": len(auto_rules),
        "semi": len(semi_rules),
        "python": len(python_rules),
        "claude": len(claude_rules),
        "unknown": len(remaining),
    }


def enhance_conditions_with_claude(rules: List[Dict], api_key: str) -> List[Dict]:
    """
    使用 Claude NLP 补全 conditions
    仅在规则库生成阶段调用一次
    """
    try:
        import anthropic
    except ImportError:
        print("  警告: anthropic 库未安装，跳过 Claude NLP 补全")
        return rules
    
    # 找出需要补全的规则
    incomplete = [
        r for r in rules 
        if r.get("check_type") == "unknown"
        or r.get("conditions", {}).get("_needs_manual_review")
    ]
    
    if not incomplete:
        return rules
    
    # 构建 prompt
    prompt_items = []
    for r in incomplete:
        prompt_items.append(
            f"Rule: {r['rule_id']}\n"
            f"  Element: {r.get('element_name', '')}\n"
            f"  Requirement: {r.get('format_requirement', '')}\n"
            f"  Detection: {r.get('detection_method', '')}\n"
        )
    
    prompt = "\n".join(prompt_items)
    
    system_prompt = """You are a format checking rule expert for Chinese academic papers.
For each rule, infer the check_type (one of: paragraph_style, global_property, 
regex_match, count_check, cross_reference, text_match, forbidden_words, ai_semantic)
and conditions (JSON object).

Output ONLY a valid JSON array, no other text. Each element should have:
- rule_id: string
- check_type: string  
- conditions: object with specific values

Example:
[{"rule_id": "COVER_01", "check_type": "paragraph_style", "conditions": {"font_name_cn": "黑体", "font_size_pt": 26}}]"""
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result_text = response.content[0].text
        
        # 解析 JSON
        import re
        json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
        if json_match:
            enhanced = json.loads(json_match.group())
            emap = {e["rule_id"]: e for e in enhanced}
            
            for rule in incomplete:
                if rule["rule_id"] in emap:
                    e = emap[rule["rule_id"]]
                    rule["check_type"] = e.get("check_type", rule["check_type"])
                    rule["conditions"] = e.get("conditions", rule["conditions"])
                    # 移除需要人工审核标记
                    rule["conditions"].pop("_needs_manual_review", None)
                    rule["conditions"].pop("_raw_requirement", None)
            
            print(f"  Claude 成功补全 {len(enhanced)} 条规则")
        else:
            print("  警告: Claude 返回格式无法解析")
            
    except Exception as e:
        print(f"  警告: Claude NLP 调用失败: {e}")
    
    return rules


def main(api_key: str = None):
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="生成规则库")
    parser.add_argument("--md", "-m", default=None, help="MD 清单路径")
    parser.add_argument("--output", "-o", default=None, help="输出 JSON 路径")
    parser.add_argument("--overrides", default=None, help="人工补丁文件路径")
    parser.add_argument("--api-key", "-k", default=None, help="Claude API Key")
    
    args = parser.parse_args()
    
    # 使用命令行参数或默认参数
    api_key = args.api_key or api_key
    
    # 默认路径
    if args.md is None:
        args.md = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "docs",
            "EMBA论文格式排版要求清单完善版.md"
        )
    
    if args.output is None:
        args.output = os.path.join(
            os.path.dirname(__file__),
            "rules_registry.json"
        )
    
    if args.overrides is None:
        args.overrides = os.path.join(
            os.path.dirname(__file__),
            "manual_overrides.json"
        )
    
    # 如果没有提供 API Key，直接跳过
    if not api_key:
        print("（跳过 Claude NLP 补全）")
    
    # 生成规则库
    generate_registry(
        md_path=args.md,
        output_path=args.output,
        overrides_path=args.overrides if os.path.exists(args.overrides) else None,
        api_key=api_key
    )


if __name__ == "__main__":
    main()  # 默认 api_key=None
