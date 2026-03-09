# -*- coding: utf-8 -*-
from docx import Document
import os

data_dir = r'D:\Projects\ThesisFormatCheck\data'

# 列出所有包含210650的文件
files = [f for f in os.listdir(data_dir) if '210650' in f]
print("Files with 210650:")
for f in sorted(files):
    print(f"  {f}")

# 找到原始备份和修复后的文件
backup_file = None
fixed_file = None

for f in files:
    full_path = os.path.join(data_dir, f)
    # 通过文件名长度和内容判断
    if f.endswith('.docx'):
        if '原文件' in f or '备份' in f:
            backup_file = full_path
        else:
            fixed_file = full_path

print(f"\nBackup: {backup_file}")
print(f"Fixed: {fixed_file}")

if backup_file and fixed_file:
    doc1 = Document(backup_file)
    doc2 = Document(fixed_file)
    print(f"\nBackup paragraphs: {len(doc1.paragraphs)}")
    print(f"Fixed paragraphs: {len(doc2.paragraphs)}")
    
    # 检查末尾段落
    print("\n=== Last 5 paragraphs of backup ===")
    for i, para in enumerate(doc1.paragraphs[-5:]):
        print(f"{len(doc1.paragraphs)-5+i}: '{para.text[:50]}'")
    
    print("\n=== Last 5 paragraphs of fixed ===")
    for i, para in enumerate(doc2.paragraphs[-5:]):
        print(f"{len(doc2.paragraphs)-5+i}: '{para.text[:50]}'")
