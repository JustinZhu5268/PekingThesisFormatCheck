# -*- coding: utf-8 -*-
"""验证流程脚本 - 第1步：修复原始文档"""
import os
import sys
import glob

# 设置路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# 添加项目根目录到路径
sys.path.insert(0, BASE_DIR)

# 导入 run_autofix 的函数（会自动处理UTF-8输出）
from run_autofix import run_fix_mode


def main():
    """第1步：查找并修复原始文档"""
    print("=" * 60)
    print("验证流程 - 第1步：修复原始文档")
    print("=" * 60)
    
    # 查找原始docx文件（不含test和已修复的）
    docx_files = glob.glob(os.path.join(DATA_DIR, '*.docx'))
    print("\n找到的文件:")
    for f in docx_files:
        print(f"  {os.path.basename(f)}")
    
    # 找到原始文件
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
            print("\n错误: 未找到原始文件")
            sys.exit(1)
    
    print(f"\n原始文件: {original_file}")
    
    # 复制到test.docx（如果不存在）
    test_file = os.path.join(DATA_DIR, 'test.docx')
    if not os.path.exists(test_file):
        import shutil
        shutil.copy(original_file, test_file)
        print(f"复制到: {test_file}")
    
    # 准备参数对象
    rules_path = os.path.join(BASE_DIR, 'emba_checker', 'rules_registry.json')
    
    class Args:
        output = None
        no_backup = False
        verbose = True
        input_file = test_file
    
    args = Args()
    
    # 调用 run_autofix.py 的修复模式
    result = run_fix_mode(test_file, rules_path, args)
    
    print("\n" + "=" * 60)
    print("第1步完成！")
    print("=" * 60)
    print("\n请继续运行 validate_step2.py 进行内容比较")
    
    return result


if __name__ == "__main__":
    sys.exit(main())
