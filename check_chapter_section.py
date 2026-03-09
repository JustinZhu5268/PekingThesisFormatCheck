# -*- coding: utf-8 -*-
"""检查文档中"第一章"具体在哪个section"""
import os
import glob
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# 找到最新的修复文件
docx_files = glob.glob('data/test_已修复_*.docx')
docx_files = [f for f in docx_files if '_原文件备份' not in f]
latest = sorted(docx_files)[-1]
print(f"检查文件: {latest}")

doc = Document(latest)

# 找到"第一章"的段落索引
chapter1_idx = None
for i, para in enumerate(doc.paragraphs):
    if '第一章' in para.text.strip():
        chapter1_idx = i
        print(f"'第一章'在段落 {i}: {para.text[:30]}...")
        break

# 分析每个section包含哪些段落
print("\n分析sections:")
sections = list(doc.sections)

# 通过遍历body的子元素来推断section边界
body = doc._body._element
children = list(body)

# 找到所有sectPr的位置
sect_pr_positions = []
for idx, child in enumerate(children):
    if child.tag.endswith('sectPr'):
        sect_pr_positions.append(idx)
        # 尝试找到这个sectPr对应的section
        for s_idx, section in enumerate(sections):
            if section._sectPr == child:
                print(f"  Section {s_idx} 在body child {idx}")
                break

print(f"\n所有sectPr位置: {sect_pr_positions}")
print(f"总sections: {len(sections)}")

# 打印每个section的pgNumType
print("\n每个section的pgNumType:")
for i, section in enumerate(sections):
    sectPr = section._sectPr
    pgNumType = sectPr.find(qn('w:pgNumType'))
    if pgNumType is not None:
        fmt = pgNumType.get(qn('w:fmt'), '无')
        start = pgNumType.get(qn('w:start'), '无')
        print(f"  Section {i}: fmt={fmt}, start={start}")
    else:
        print(f"  Section {i}: 无pgNumType")
