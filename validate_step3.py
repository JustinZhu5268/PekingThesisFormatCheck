# -*- coding: utf-8 -*-
"""验证流程脚本 - 第3步：检查格式修复效果"""
import os
import glob
import sys

# 设置UTF-8输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
sys.path.insert(0, BASE_DIR)

import json
from docx import Document
from emba_checker.zone_detector import ZoneDetector
from emba_checker.docx_engine import DocxEngine


def run_check(input_file: str):
    """检查模式：只检查格式问题，不修复"""
    print(f"\n检查文件: {os.path.basename(input_file)}")
    print("=" * 60)
    
    # 加载文档
    doc = Document(input_file)
    
    # 区域检测
    zone_detector = ZoneDetector(doc)
    zone_map = zone_detector.zone_map
    
    # 加载规则
    rules_path = os.path.join(BASE_DIR, 'emba_checker', 'rules_registry.json')
    with open(rules_path, 'r', encoding='utf-8') as f:
        rules = json.load(f)
    
    # 只选择自动执行的规则
    enabled_rules = [r for r in rules if r.get("enabled", True)]
    
    print(f"加载了 {len(enabled_rules)} 条规则")
    print(f"文档共有 {len(doc.paragraphs)} 个段落\n")
    
    # 运行检查
    engine = DocxEngine(doc, enabled_rules, zone_map)
    issues = engine.run_all()
    
    # 统计结果
    error_count = sum(1 for i in issues if getattr(i, 'severity', '') == 'error')
    warning_count = sum(1 for i in issues if getattr(i, 'severity', '') == 'warning')
    info_count = sum(1 for i in issues if getattr(i, 'severity', '') == 'info')
    
    print("=" * 60)
    print("格式检查结果")
    print("=" * 60)
    print(f"发现问题总数: {len(issues)}")
    print(f"  错误: {error_count}")
    print(f"  警告: {warning_count}")
    print(f"  信息: {info_count}")
    print("=" * 60)
    
    # 显示所有问题
    if issues:
        print("\n详细问题列表:")
        print("-" * 60)
        for i, issue in enumerate(issues, 1):
            rule_id = getattr(issue, 'rule_id', '?')
            severity = getattr(issue, 'severity', 'info')
            message = getattr(issue, 'message', '')
            # 简化消息显示
            message = message.split('\n')[0][:80] if message else ""
            print(f"{i:3}. [{severity}] {rule_id}: {message}")
    else:
        print("\n未发现问题！")
    
    # 结论
    print("\n" + "=" * 60)
    print("结论:")
    print("=" * 60)
    if error_count == 0 and warning_count == 0:
        print("✓ 格式修复成功！没有发现错误和警告")
    elif error_count == 0:
        print("✓ 没有错误，但有警告")
    else:
        print("✗ 仍存在格式错误，需要继续修复")
    
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    # 查找修复后的文件（不含"原文件备份"）
    fixed_files = [f for f in glob.glob(os.path.join(DATA_DIR, 'test_已修复_*.docx')) 
                   if '原文件备份' not in f]
    
    if not fixed_files:
        print("错误: 未找到修复后的文件")
        print("请先运行 validate_step1.py 进行修复")
        sys.exit(1)
    
    fixed = fixed_files[-1]  # 最新的修复文件
    
    result = run_check(fixed)
    sys.exit(result)
