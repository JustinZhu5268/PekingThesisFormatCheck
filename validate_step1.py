# -*- coding: utf-8 -*-
"""验证流程脚本 - 第1步：修复原始文档"""
import os
import glob
import shutil
import sys

# 设置UTF-8输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 设置路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# 查找原始docx文件
docx_files = glob.glob(os.path.join(DATA_DIR, '*.docx'))
print("找到的文件:")
for f in docx_files:
    print(f"  {os.path.basename(f)}")

# 找到原始文件（不含test和已修复的）
original_file = None
for f in docx_files:
    basename = os.path.basename(f)
    if 'test' not in basename.lower() and '已修复' not in basename and '_fixed' not in basename.lower():
        original_file = f
        break

if not original_file:
    # 备选：使用test.docx
    test_file = os.path.join(DATA_DIR, 'test.docx')
    if os.path.exists(test_file):
        original_file = test_file
    else:
        print("错误: 未找到原始文件")
        sys.exit(1)

print(f"\n原始文件: {original_file}")

# 复制到test.docx（如果不存在）
test_file = os.path.join(DATA_DIR, 'test.docx')
if not os.path.exists(test_file):
    shutil.copy(original_file, test_file)
    print(f"复制到: {test_file}")
    print(f"文件大小: {os.path.getsize(test_file)} bytes")

# 现在运行修复
print("\n" + "="*60)
print("开始修复...")
print("="*60)

# 切换到项目目录运行
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

from emba_checker.docx_autofixer import auto_fix

rules_path = os.path.join(BASE_DIR, 'emba_checker', 'rules_registry.json')

output_path, report = auto_fix(
    test_file,
    rules_path,
    output_path=None,
    backup=True,
    verbose=True
)

# 输出摘要
summary = report.get_summary()

print("\n" + "=" * 60)
print("修复完成")
print("=" * 60)
print(f"输出文件: {output_path}")
print(f"总修复项: {summary['total_fixes']}")
print(f"  成功: {summary['successful_fixes']}")
print(f"  失败: {summary['failed_fixes']}")
print("=" * 60)

# 保存修复报告
report_path = output_path.replace(".docx", "_修复报告.txt")
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report.to_string())

print(f"\n修复报告: {report_path}")
print("\n请继续运行 validate_step2.py 进行内容比较")
