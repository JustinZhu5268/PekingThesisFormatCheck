# -*- coding: utf-8 -*-
"""验证流程脚本 - 第2步：比较内容差异"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
sys.path.insert(0, BASE_DIR)

# 导入 run_autofix 的函数（会自动处理UTF-8输出）
from run_autofix import run_verify_mode


def main():
    """第2步：验证修复后的内容差异"""
    print("=" * 60)
    print("验证流程 - 第2步：内容差异比较")
    print("=" * 60)
    
    # 查找修复后的文件（不含"原文件备份"）
    import glob
    fixed_files = [f for f in glob.glob(os.path.join(DATA_DIR, 'test_已修复_*.docx')) 
                   if '原文件' not in f and '备份' not in f]
    
    if not fixed_files:
        print("\n错误: 未找到修复后的文件")
        print("请先运行 validate_step1.py 进行修复")
        sys.exit(1)
    
    # 最新的修复文件
    fixed_file = max(fixed_files, key=os.path.getmtime)
    print(f"\n修复文件: {fixed_file}")
    
    # 调用 run_autofix.py 的验证模式
    result = run_verify_mode(fixed_file)
    
    print("\n" + "=" * 60)
    print("第2步完成！")
    print("=" * 60)
    print("\n请继续运行 validate_step3.py 进行格式检查")
    
    return result


if __name__ == "__main__":
    sys.exit(main())
