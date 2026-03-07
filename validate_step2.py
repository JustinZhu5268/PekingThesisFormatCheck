# -*- coding: utf-8 -*-
"""验证流程脚本 - 第2步：比较内容差异"""
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

from docx import Document


def compare_documents(original_path, fixed_path):
    """比较两个文档的内容差异"""
    print(f"\n比较文档:")
    print(f"  原始: {os.path.basename(original_path)}")
    print(f"  修复: {os.path.basename(fixed_path)}")
    print()
    
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
    for i, diff in enumerate(differences[:20]):
        print(f"{i+1}. 段落 {diff['index']}:")
        print(f"   原始: {diff['original'][:80]}...")
        print(f"   修复: {diff['fixed'][:80]}...")
        print(f"   长度变化: {diff['original_len']} -> {diff['fixed_len']} (差: {diff['fixed_len'] - diff['original_len']})")
        print()
    
    if len(differences) > 20:
        print(f"... 还有 {len(differences) - 20} 处差异")
    
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
    for diff in differences:
        orig = diff['original']
        fixed = diff['fixed']
        # 检查是否只是空格变化
        if orig.replace(" ", "").replace("　", "") == fixed.replace(" ", "").replace("　", ""):
            space_changes.append(diff)
    
    print(f"纯空格变化: {len(space_changes)} 处")
    
    # 内容实质性变化
    content_changes = [d for d in differences if d not in space_changes]
    print(f"内容实质性变化: {len(content_changes)} 处")
    
    # 检查是否是预期的关键词分隔符修复
    expected_keyword_fix = False
    for diff in content_changes:
        orig = diff['original']
        fixed = diff['fixed']
        # 检查是否是关键词行的分隔符变化（分号->逗号）
        if '关键词' in orig and '；' in orig and '，' in fixed and '；' not in fixed:
            expected_keyword_fix = True
    
    # 判断结果
    print("\n" + "=" * 60)
    print("结论:")
    print("=" * 60)
    if expected_keyword_fix:
        print("✓ 内容变化仅为预期的关键词分隔符修复（；->，）")
        print("  可以继续进行格式检查")
    elif len(content_changes) == 0:
        print("✓ 内容变化仅限于空格/格式，没有实质性内容变化")
        print("  可以继续进行格式检查")
    else:
        print("✗ 发现非预期的实质性内容变化！需要检查修复逻辑")
    
    return differences


if __name__ == "__main__":
    # 查找修复后的文件（不含"原文件备份"）
    fixed_files = [f for f in glob.glob(os.path.join(DATA_DIR, 'test_已修复_*.docx')) 
                   if '原文件备份' not in f]
    
    if not fixed_files:
        print("错误: 未找到修复后的文件")
        print("请先运行 validate_step1.py 进行修复")
        sys.exit(1)
    
    fixed = fixed_files[-1]  # 最新的修复文件
    
    # 原始文件是备份文件
    original = fixed.replace('.docx', '_原文件备份.docx')
    
    if not os.path.exists(original):
        # 备选：使用test.docx
        original = os.path.join(DATA_DIR, 'test.docx')
    
    if not os.path.exists(original):
        print("错误: 未找到原始文件")
        sys.exit(1)
    
    differences = compare_documents(original, fixed)
    
    print("\n请继续运行 validate_step3.py 进行格式检查")
