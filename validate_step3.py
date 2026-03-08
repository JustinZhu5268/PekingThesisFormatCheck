# -*- coding: utf-8 -*-
"""验证流程脚本 - 第3步：检查格式修复效果"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
sys.path.insert(0, BASE_DIR)

# 导入 run_autofix 的函数（会自动处理UTF-8输出）
from run_autofix import run_check_mode


def main():
    """第3步：检查格式修复效果"""
    print("=" * 60)
    print("验证流程 - 第3步：格式检查")
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
    print(f"\n检查文件: {fixed_file}")
    
    # 规则文件路径
    rules_path = os.path.join(BASE_DIR, 'emba_checker', 'rules_registry.json')
    
    # 调用 run_autofix.py 的检查模式
    result = run_check_mode(fixed_file, rules_path, verbose=True)
    
    print("\n" + "=" * 60)
    if result == 0:
        print("第3步完成！格式检查通过 ✓")
    else:
        print("第3步完成！格式检查未通过")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    sys.exit(main())
