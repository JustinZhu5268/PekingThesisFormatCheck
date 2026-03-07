# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 覆盖率核对脚本
验证 MD 清单与规则库的双向覆盖
"""

import json
import os
import sys
import re
from typing import List, Set, Dict, Tuple

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def parse_md_keys(md_path: str) -> Set[str]:
    """
    从 MD 清单中提取所有可编程规则的 md_source_key
    格式: "{章节名}::{要素名}"
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    keys = set()
    current_section = None
    
    lines = content.split('\n')
    for line in lines:
        stripped = line.strip()
        
        # 识别章节标题 (## 开头)
        if stripped.startswith('## '):
            # 跳过元信息行
            if '附：' in stripped or '可编程' in stripped or stripped.startswith('>'):
                continue
            # 提取章节名
            current_section = stripped.lstrip('#').strip()
            continue
        
        # 跳过非表格行
        if not stripped.startswith('|'):
            continue
        if '---' in stripped or '要素' in stripped[:20]:
            continue
        
        # 解析表格列
        cells = [c.strip() for c in stripped.split('|') if c.strip()]
        if len(cells) < 4:
            continue
        
        element_name = cells[0].replace('**', '')
        programmability = cells[3].strip()
        
        # 只保留 ✅ 和 ⚠️
        is_auto = '\u2705' in programmability
        is_semi = '\u26a0' in programmability
        if not is_auto and not is_semi:
            continue
        
        # 生成 md_source_key
        if current_section:
            key = f"{current_section}::{element_name}"
            keys.add(key)
    
    return keys


def parse_registry_keys(registry_path: str) -> Set[str]:
    """
    从规则库中提取所有 md_source_key
    """
    with open(registry_path, 'r', encoding='utf-8') as f:
        rules = json.load(f)
    
    keys = set()
    for rule in rules:
        key = rule.get('md_source_key')
        if key:
            keys.add(key)
    
    return keys


def verify_coverage(md_path: str, registry_path: str) -> Tuple[Set[str], Set[str]]:
    """
    验证 MD 清单与规则库的双向覆盖
    
    Returns:
        (missing_in_registry, orphan_in_registry)
        - missing_in_registry: MD 有但规则库没有的 key
        - orphan_in_registry: 规则库有但 MD 没有的 key
    """
    md_keys = parse_md_keys(md_path)
    registry_keys = parse_registry_keys(registry_path)
    
    missing_in_registry = md_keys - registry_keys
    orphan_in_registry = registry_keys - md_keys
    
    return missing_in_registry, orphan_in_registry


def generate_coverage_report(
    missing_in_registry: Set[str],
    orphan_in_registry: Set[str],
    output_path: str = None,
    md_path: str = None,
    registry_path: str = None
) -> str:
    """
    生成覆盖率报告
    
    Returns:
        报告文本
    """
    lines = []
    lines.append("=" * 60)
    lines.append("MD 清单 ↔ 规则库 覆盖率核对报告")
    lines.append("=" * 60)
    lines.append("")
    
    # 使用传入的路径或默认值
    if md_path is None:
        md_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "docs",
            "EMBA论文格式排版要求清单完善版.md"
        )
    if registry_path is None:
        registry_path = os.path.join(
            os.path.dirname(__file__),
            "rules_registry.json"
        )
    
    md_keys = parse_md_keys(md_path)
    registry_keys = parse_registry_keys(registry_path)
    
    total_md = len(md_keys)
    total_registry = len(registry_keys)
    matched = len(md_keys & registry_keys)
    
    lines.append(f"MD 清单规则数: {total_md}")
    lines.append(f"规则库规则数: {total_registry}")
    lines.append(f"匹配数: {matched}")
    lines.append(f"覆盖率: {matched}/{total_md} = {matched*100/total_md:.1f}%" if total_md > 0 else "N/A")
    lines.append("")
    
    # 缺失规则
    if missing_in_registry:
        lines.append("=" * 60)
        lines.append(f"⚠️ 缺失规则 ({len(missing_in_registry)} 条) - MD有但规则库没有:")
        lines.append("=" * 60)
        for key in sorted(missing_in_registry):
            lines.append(f"  - {key}")
        lines.append("")
    
    # 孤儿规则
    if orphan_in_registry:
        lines.append("=" * 60)
        lines.append(f"⚠️ 孤儿规则 ({len(orphan_in_registry)} 条) - 规则库有但MD没有:")
        lines.append("=" * 60)
        for key in sorted(orphan_in_registry):
            lines.append(f"  - {key}")
        lines.append("")
    
    # 总结
    lines.append("=" * 60)
    if not missing_in_registry and not orphan_in_registry:
        lines.append("✓ 覆盖率核对通过！")
    else:
        lines.append("✗ 覆盖率核对失败！")
    lines.append("=" * 60)
    
    report = "\n".join(lines)
    
    # 写入文件
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
    
    return report


def verify_and_block(md_path: str, registry_path: str) -> bool:
    """
    启动前调用。覆盖率不足则 raise SystemExit
    
    Args:
        md_path: MD 清单路径
        registry_path: 规则库路径
        
    Returns:
        True if pass
        
    Raises:
        SystemExit: 覆盖率不足
    """
    missing, orphan = verify_coverage(md_path, registry_path)
    
    if missing or orphan:
        report = generate_coverage_report(missing, orphan, 'coverage_report.txt')
        print(report)
        raise SystemExit(f"覆盖率核对失败！详见 coverage_report.txt")
    
    print("=" * 60)
    print("✓ 覆盖率核对通过！")
    print("=" * 60)
    return True


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="覆盖率核对")
    parser.add_argument("--md", "-m", default=None, help="MD 清单路径")
    parser.add_argument("--registry", "-r", default=None, help="规则库路径")
    parser.add_argument("--report", default=None, help="报告输出路径")
    
    args = parser.parse_args()
    
    # 默认路径
    if args.md is None:
        args.md = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "docs",
            "EMBA论文格式排版要求清单完善版.md"
        )
    
    if args.registry is None:
        args.registry = os.path.join(
            os.path.dirname(__file__),
            "rules_registry.json"
        )
    
    # 运行核对
    missing, orphan = verify_coverage(args.md, args.registry)
    
    # 生成报告
    report = generate_coverage_report(missing, orphan, args.report)
    print(report)
    
    # 返回状态码
    if missing or orphan:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
