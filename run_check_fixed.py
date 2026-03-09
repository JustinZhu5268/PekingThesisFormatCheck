# -*- coding: utf-8 -*-
"""
运行规则检查 - 验证修复后的文档格式
使用 DocxEngine
"""
import sys
import os
import io
import json

# 设置UTF-8输出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from docx import Document
from emba_checker.zone_detector import ZoneDetector
from emba_checker.docx_engine import DocxEngine


def run_check(doc_path, rules_path):
    """运行规则检查"""
    # 加载文档
    doc = Document(doc_path)
    
    # 区域检测
    zone_detector = ZoneDetector(doc)
    zone_map = zone_detector.zone_map
    
    # 加载规则
    with open(rules_path, 'r', encoding='utf-8') as f:
        rules = json.load(f)
    
    # 只选择自动执行的规则
    enabled_rules = [r for r in rules if r.get("enabled", True)]
    
    # 运行检查
    engine = DocxEngine(doc, enabled_rules, zone_map)
    issues = engine.run_all()
    
    return issues


if __name__ == "__main__":
    # 检查原始文档作为对比
    original_doc = "data/医保支付方式改革下A医疗集团医疗收入质量优化研究——以A医疗集团为例-定稿V1.0.docx"
    fixed_doc = "data/医保支付方式改革下A医疗集团医疗收入质量优化研究——以A医疗集团为例-定稿V1.0_已修复_20260307_143617.docx"
    rules_path = "emba_checker/rules_registry.json"
    
    print("=" * 60)
    print("对比检查：原始文档 vs 修复后文档")
    print("=" * 60)
    
    # 检查原始文档
    print("\n【原始文档检查】")
    print(f"文档: {original_doc}")
    print("-" * 60)
    
    issues_original = run_check(original_doc, rules_path)
    
    error_count = sum(1 for i in issues_original if getattr(i, 'severity', '') == 'error')
    warning_count = sum(1 for i in issues_original if getattr(i, 'severity', '') == 'warning')
    info_count = sum(1 for i in issues_original if getattr(i, 'severity', '') == 'info')
    
    print(f"\n发现问题总数: {len(issues_original)}")
    print(f"  错误: {error_count}")
    print(f"  警告: {warning_count}")
    print(f"  信息: {info_count}")
    
    # 显示前20个问题
    if issues_original:
        print("\n原始文档前20个问题:")
        print("-" * 60)
        for i, issue in enumerate(issues_original[:20]):
            rule_id = getattr(issue, 'rule_id', '?')
            severity = getattr(issue, 'severity', 'info')
            message = getattr(issue, 'message', '')[:60]
            print(f"{i+1}. [{severity}] {rule_id}: {message}...")
        
        if len(issues_original) > 20:
            print(f"... 还有 {len(issues_original) - 20} 个问题")
    else:
        print("\n原始文档没有问题！")
    
    # 检查修复后的文档
    print("\n" + "=" * 60)
    print("【修复后文档检查】")
    print("-" * 60)
    
    issues_fixed = run_check(fixed_doc, rules_path)
    
    error_count = sum(1 for i in issues_fixed if getattr(i, 'severity', '') == 'error')
    warning_count = sum(1 for i in issues_fixed if getattr(i, 'severity', '') == 'warning')
    info_count = sum(1 for i in issues_fixed if getattr(i, 'severity', '') == 'info')
    
    print(f"\n发现问题总数: {len(issues_fixed)}")
    print(f"  错误: {error_count}")
    print(f"  警告: {warning_count}")
    print(f"  信息: {info_count}")
    
    # 显示前20个问题
    if issues_fixed:
        print("\n修复后文档前20个问题:")
        print("-" * 60)
        for i, issue in enumerate(issues_fixed[:20]):
            rule_id = getattr(issue, 'rule_id', '?')
            severity = getattr(issue, 'severity', 'info')
            message = getattr(issue, 'message', '')[:60]
            print(f"{i+1}. [{severity}] {rule_id}: {message}...")
        
        if len(issues_fixed) > 20:
            print(f"... 还有 {len(issues_fixed) - 20} 个问题")
    else:
        print("\n修复后文档没有问题！")
    
    # 对比结果
    print("\n" + "=" * 60)
    print("【对比结果】")
    print("=" * 60)
    print(f"原始文档问题数: {len(issues_original)}")
    print(f"修复后文档问题数: {len(issues_fixed)}")
    print(f"减少: {len(issues_original) - len(issues_fixed)} 个问题")
