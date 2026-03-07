# -*- coding: utf-8 -*-
"""
比较原始论文和修复后论文的内容差异
"""
import sys
import os
import io

# 设置UTF-8输出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from docx import Document


def compare_documents(original_path, fixed_path):
    """比较两个文档的内容差异"""
    doc1 = Document(original_path)
    doc2 = Document(fixed_path)
    
    paragraphs1 = [p.text.strip() for p in doc1.paragraphs]
    paragraphs2 = [p.text.strip() for p in doc2.paragraphs]
    
    print(f"原始文档段落数: {len(paragraphs1)}")
    print(f"修复文档段落数: {len(paragraphs2)}")
    print("=" * 60)
    
    # 找出差异
    differences = []
    
    max_len = max(len(paragraphs1), len(paragraphs2))
    
    for i in range(max_len):
        p1 = paragraphs1[i] if i < len(paragraphs1) else "[不存在]"
        p2 = paragraphs2[i] if i < len(paragraphs2) else "[不存在]"
        
        if p1 != p2:
            differences.append({
                'index': i,
                'original': p1,
                'fixed': p2,
                'original_len': len(p1),
                'fixed_len': len(p2)
            })
    
    print(f"\n发现 {len(differences)} 处差异:\n")
    
    # 显示前20个差异
    for i, diff in enumerate(differences[:50]):
        print(f"{i+1}. 段落 {diff['index']}:")
        print(f"   原始: {diff['original'][:80]}...")
        print(f"   修复: {diff['fixed'][:80]}...")
        print(f"   长度变化: {diff['original_len']} -> {diff['fixed_len']} (差: {diff['fixed_len'] - diff['original_len']})")
        print()
    
    if len(differences) > 50:
        print(f"... 还有 {len(differences) - 50} 处差异")
    
    # 特别检查关键词分隔符相关的变化
    print("\n" + "=" * 60)
    print("关键词相关段落检查:")
    print("=" * 60)
    
    for i, p in enumerate(paragraphs1):
        if "关键词" in p:
            p2 = paragraphs2[i] if i < len(paragraphs2) else ""
            if p != p2:
                print(f"\n段落 {i}:")
                print(f"  原始: {p}")
                print(f"  修复: {p2}")
    
    # 检查空格相关变化
    print("\n" + "=" * 60)
    print("空格变化统计:")
    print("=" * 60)
    
    space_changes = []
    for i, diff in enumerate(differences):
        orig = diff['original']
        fixed = diff['fixed']
        # 检查是否只是空格变化
        if orig.replace(" ", "").replace("　", "") == fixed.replace(" ", "").replace("　", ""):
            space_changes.append(diff)
    
    print(f"纯空格变化: {len(space_changes)} 处")
    
    # 内容实质性变化
    content_changes = [d for d in differences if d not in space_changes]
    print(f"内容实质性变化: {len(content_changes)} 处")
    
    return differences


if __name__ == "__main__":
    # 使用最新的修复文件
    original = "data/医保支付方式改革下A医疗集团医疗收入质量优化研究——以A医疗集团为例-定稿V1.0.docx"
    fixed = "data/医保支付方式改革下A医疗集团医疗收入质量优化研究——以A医疗集团为例-定稿V1.0_已修复_20260307_153154.docx"
    
    differences = compare_documents(original, fixed)
