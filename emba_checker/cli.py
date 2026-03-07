# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 命令行模块
提供与 GUI 相同的功能，但以命令行界面呈现
"""

import os
import sys
import shutil
import argparse
from datetime import datetime
from typing import List, Any, Optional

# 添加项目根目录到路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='北大光华 EMBA 论文格式审查工具 - 命令行版',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s input.docx                                    # 基本用法
  %(prog)s input.docx -r rules_registry.json             # 指定规则文件
  %(prog)s input.docx -k your-api-key                   # 启用 AI 检查
  %(prog)s input.docx -o ./output                        # 指定输出目录
  %(prog)s input.docx --level critical                  # 只检查严重问题
  %(prog)s input.docx --no-ai                           # 禁用 AI 检查
  %(prog)s input.docx -v                                 # 显示详细日志
        """
    )
    
    # 位置参数
    parser.add_argument(
        'input_file',
        nargs='?',
        help='输入的 Word 文档路径 (.docx)'
    )
    
    # 可选参数
    parser.add_argument(
        '-r', '--rules',
        default=None,
        help='规则文件路径 (默认: rules_registry.json)'
    )
    
    parser.add_argument(
        '-k', '--api-key',
        default=None,
        help='Claude API Key (用于 AI 语义检查)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='输出目录 (默认: 当前目录)'
    )
    
    parser.add_argument(
        '--level',
        choices=['critical', 'important', 'all'],
        default='all',
        help='检查级别: critical(仅必须项), important(重要及以上), all(全部规则)'
    )
    
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='禁用 AI 语义检查'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细日志'
    )
    
    parser.add_argument(
        '--export-json',
        default=None,
        help='导出 Issue 到 JSON 文件'
    )
    
    return parser.parse_args()


def get_default_rules_path():
    """获取默认规则文件路径"""
    # 优先使用 emba_checker 目录下的规则文件
    default_paths = [
        os.path.join(BASE_DIR, 'emba_checker', 'rules_registry.json'),
        os.path.join(BASE_DIR, 'rules_registry.json'),
    ]
    
    for path in default_paths:
        if os.path.exists(path):
            return path
    
    return default_paths[0]


def generate_output(doc_path: str, issues: List[Any], output_dir: Optional[str] = None) -> tuple:
    """
    生成输出文件（标注文档 + 报告）
    
    Returns:
        (output_docx, output_report): 输出文件路径元组
    """
    from emba_checker.safe_annotator import SafeAnnotator, generate_report as gen_report
    from docx import Document
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    basename = os.path.splitext(os.path.basename(doc_path))[0]
    
    # 确定输出目录
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(doc_path))
        if not output_dir:
            output_dir = '.'
    
    # 输出文件路径
    output_docx = os.path.join(output_dir, f"{basename}_审查结果_{timestamp}.docx")
    output_report = os.path.join(output_dir, f"{basename}_审查报告_{timestamp}.txt")
    
    # 复制并标注文档
    print(f"\n正在生成标注文档: {output_docx}")
    shutil.copy2(doc_path, output_docx)
    doc = Document(output_docx)
    
    # 标注
    annotator = SafeAnnotator(doc, issues, output_docx)
    annotated, failed = annotator.annotate_all()
    doc.save(output_docx)
    
    print(f"  标注完成: {annotated} 个段落已标注, {failed} 个失败")
    
    # 生成报告
    print(f"正在生成报告: {output_report}")
    gen_report(doc_path, issues, output_report)
    
    return output_docx, output_report


def main():
    """主入口"""
    args = parse_args()
    
    # 显示帮助信息
    if args.input_file is None:
        parse_args(['--help'])
        return 0
    
    # 验证输入文件
    if not os.path.exists(args.input_file):
        print(f"错误: 输入文件不存在: {args.input_file}", file=sys.stderr)
        return 1
    
    # 验证文件扩展名
    if not args.input_file.lower().endswith('.docx'):
        print(f"错误: 输入文件必须是 .docx 格式", file=sys.stderr)
        return 1
    
    # 获取规则文件路径
    rules_path = args.rules if args.rules else get_default_rules_path()
    if not os.path.exists(rules_path):
        print(f"错误: 规则文件不存在: {rules_path}", file=sys.stderr)
        return 1
    
    # 确定输出目录
    output_dir = args.output if args.output else None
    
    # 打印配置信息
    print("=" * 60)
    print("北大光华 EMBA 论文格式审查工具 - 命令行版")
    print("=" * 60)
    print(f"论文文件: {args.input_file}")
    print(f"规则文件: {rules_path}")
    print(f"检查级别: {args.level}")
    print(f"AI 检查: {'启用' if not args.no_ai and args.api_key else '禁用'}")
    if output_dir:
        print(f"输出目录: {output_dir}")
    print("-" * 60)
    
    # 进度回调
    def progress_callback(source, message, current=None, total=None):
        if args.verbose:
            if total:
                print(f"[{source}] {message} ({current}/{total})")
            else:
                print(f"[{source}] {message}")
        else:
            # 简单进度显示
            if total and total > 0 and current is not None:
                pct = int(current / total * 100)
                if pct % 20 == 0:  # 每 20% 显示一次
                    print(f"[{source}] {message} - {pct}%")
    
    try:
        # 导入并创建引擎
        from emba_checker.main_engine import MainEngine
        
        print("\n加载规则库...")
        engine = MainEngine(
            args.input_file,
            rules_path,
            args.api_key,
            progress_callback
        )
        
        # 运行审查
        print("\n开始审查...\n")
        enable_claude = not args.no_ai and args.api_key is not None
        issues = engine.run(enable_claude=enable_claude)
        
        # 获取摘要
        summary = engine.get_summary()
        
        # 输出摘要
        print("\n" + "=" * 60)
        print("审查完成")
        print("=" * 60)
        print(f"发现问题总数: {summary['total_issues']}")
        print(f"  ★★★★★ 错误: {summary['error_count']}")
        print(f"  ★★★★☆ 警告: {summary['warning_count']}")
        print(f"  ★★★☆☆ 信息: {summary['info_count']}")
        print(f"\n确定性检查: {summary['docx_engine_issues']} 条")
        print(f"AI 语义检查: {summary['claude_engine_issues']} 条")
        print(f"去重合并: {summary['deduplicated']} 条")
        print(f"总耗时: {summary['total_time']:.2f} 秒")
        print("=" * 60)
        
        # 生成输出文件
        if issues:
            output_docx, output_report = generate_output(
                args.input_file, issues, output_dir
            )
            
            print(f"\n输出文件:")
            print(f"  标注文档: {output_docx}")
            print(f"  审查报告: {output_report}")
        else:
            print("\n未发现问题!")
        
        # 导出 JSON
        if args.export_json:
            engine.export_issues_json(args.export_json)
            print(f"\n已导出 Issue 到: {args.export_json}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n操作已取消", file=sys.stderr)
        return 130
        
    except Exception as e:
        print(f"\n错误: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
