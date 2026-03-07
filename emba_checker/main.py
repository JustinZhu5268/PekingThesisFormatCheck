# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 主入口
"""

import sys
import os

# 添加项目根目录到路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from emba_checker.gui import main as gui_main


def main():
    """主入口函数"""
    gui_main()


if __name__ == "__main__":
    main()
