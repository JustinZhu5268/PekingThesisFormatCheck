# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 自动修复 CLI 入口
"""

import sys
import os
import glob
import io
import argparse

# 设置UTF-8输出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='EMBA 论文格式自动修复工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python run_autofix.py input.docx                    # 修复文档
  python run_autofix.py input.docx -o ./output        # 指定输出目录
  python run_autofix.py input.docx --no-backup       # 不备份原文件
  python run_autofix.py input.docx -v                # 显示详细日志
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
        '-o', '--output',
        default=None,
        help='输出目录 (默认: 当前目录)'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='不备份原文件'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细日志'
    )
    
    parser.add_argument(
        '-r', '--rules',
        default=None,
        help='规则文件路径 (默认: rules_registry.json)'
    )
    
    parser.add_argument(
        '-c', '--check',
        action='store_true',
        help='只检查格式问题，不修复（验证模式）'
    )

    parser.add_argument(
        '--diff',
        action='store_true',
        help='对比原始文档和修复后文档的格式差异（需要提供两个文件）'
    )

    parser.add_argument(
        '--inspect',
        action='store_true',
        help='检查文档的实际格式（封面、标题、关键词等）'
    )

    parser.add_argument(
        '--original',
        default=None,
        help='原始文档路径（用于--diff模式）'
    )

    return parser.parse_args()


def run_check_mode(input_file: str, rules_path: str, verbose: bool = False):
    """检查模式：只检查格式问题，不修复"""
    import json
    from docx import Document
    from emba_checker.zone_detector import ZoneDetector
    from emba_checker.docx_engine import DocxEngine
    
    print("\n开始格式检查...\n")
    
    # 加载文档
    doc = Document(input_file)
    
    # 区域检测
    zone_detector = ZoneDetector(doc)
    zone_map = zone_detector.zone_map
    
    # 加载规则
    with open(rules_path, 'r', encoding='utf-8') as f:
        rules = json.load(f)
    
    # 只选择自动执行的规则
    enabled_rules = [r for r in rules if r.get("enabled", True)]
    
    print(f"加载了 {len(enabled_rules)} 条规则")
    print(f"文档共有 {len(doc.paragraphs)} 个段落\n")
    
    # 运行检查
    engine = DocxEngine(doc, enabled_rules, zone_map)
    issues = engine.run_all()
    
    # 统计结果
    error_count = sum(1 for i in issues if getattr(i, 'severity', '') == 'error')
    warning_count = sum(1 for i in issues if getattr(i, 'severity', '') == 'warning')
    info_count = sum(1 for i in issues if getattr(i, 'severity', '') == 'info')
    
    print("=" * 60)
    print("格式检查结果")
    print("=" * 60)
    print(f"发现问题总数: {len(issues)}")
    print(f"  错误: {error_count}")
    print(f"  警告: {warning_count}")
    print(f"  信息: {info_count}")
    print("=" * 60)
    
    # 显示所有问题
    if issues:
        print("\n详细问题列表:")
        print("-" * 60)
        for i, issue in enumerate(issues, 1):
            rule_id = getattr(issue, 'rule_id', '?')
            severity = getattr(issue, 'severity', 'info')
            message = getattr(issue, 'message', '')
            # 简化消息显示
            message = message.split('\n')[0][:80] if message else ""
            print(f"{i:3}. [{severity}] {rule_id}: {message}")
    else:
        print("\n未发现问题！")
    
    return 0 if not issues else 1


def run_diff_mode(input_file: str, original_file: str = None):
    """对比模式：对比原始文档和修复后文档的格式差异"""
    from docx import Document
    from emba_checker import utils

    print("\n开始格式对比...\n")

    # 如果没有指定原始文件，尝试自动查找
    if not original_file:
        # 尝试查找data目录下的原始文件
        data_dir = os.path.dirname(input_file) if input_file else 'data'
        if not data_dir:
            data_dir = 'data'

        # 查找可能的原始文件（不含"已修复"或"_fixed"字样）
        import glob as g
        all_files = g.glob(os.path.join(data_dir, '*.docx'))

        for f in all_files:
            basename = os.path.basename(f)
            if '已修复' not in basename and '_fixed' not in basename and basename != os.path.basename(input_file):
                original_file = f
                break

    if not original_file or not os.path.exists(original_file):
        print(f"错误: 原始文件不存在: {original_file}", file=sys.stderr)
        return 1

    print(f"原始文件: {original_file}")
    print(f"修复后文件: {input_file}\n")

    doc_orig = Document(original_file)
    doc_fixed = Document(input_file)

    # 检查正文段落对齐方式
    print("=" * 60)
    print("正文段落对齐方式对比")
    print("=" * 60)
    for i in range(20, 40):
        text = doc_orig.paragraphs[i].text.strip()
        if len(text) > 50:
            align_orig = utils.get_paragraph_alignment(doc_orig.paragraphs[i])
            align_fixed = utils.get_paragraph_alignment(doc_fixed.paragraphs[i])
            indent_orig = utils.get_first_line_indent(doc_orig.paragraphs[i])
            indent_fixed = utils.get_first_line_indent(doc_fixed.paragraphs[i])

            print(f"段落 {i}: {text[:40]}...")
            print(f"  原始对齐: {align_orig}, 首行缩进: {indent_orig}")
            print(f"  修复后对齐: {align_fixed}, 首行缩进: {indent_fixed}")

            if align_orig != align_fixed:
                print(f"  ❌ 对齐方式被改变了!")
            if indent_orig != indent_fixed:
                print(f"  ❌ 首行缩进被改变了!")
            print()
            break

    # 检查关键词
    print("=" * 60)
    print("关键词对比")
    print("=" * 60)
    for i in range(len(doc_orig.paragraphs)):
        text = doc_orig.paragraphs[i].text.strip()
        if "关键词" in text and "：" in text:
            print(f"原始: {text}")
            print(f"修复后: {doc_fixed.paragraphs[i].text.strip()}")
            print()
            break

    # 检查摘要标题格式
    print("=" * 60)
    print("摘要标题格式对比")
    print("=" * 60)
    for i in range(len(doc_orig.paragraphs)):
        text = doc_orig.paragraphs[i].text.strip()
        if text == "摘要":
            print(f"段落 {i}: {text}")
            align_orig = utils.get_paragraph_alignment(doc_orig.paragraphs[i])
            align_fixed = utils.get_paragraph_alignment(doc_fixed.paragraphs[i])
            for run in doc_orig.paragraphs[i].runs:
                if run.text.strip():
                    size_orig = utils.get_font_size(run)
                    break
            for run in doc_fixed.paragraphs[i].runs:
                if run.text.strip():
                    size_fixed = utils.get_font_size(run)
                    break
            print(f"  原始对齐: {align_orig}, 字号: {size_orig}")
            print(f"  修复后对齐: {align_fixed}, 字号: {size_fixed}")
            print()
            break

    return 0


def run_inspect_mode(input_file: str):
    """检查模式：检查文档的实际格式"""
    from docx import Document
    from emba_checker import utils

    print("\n开始检查文档格式...\n")

    doc = Document(input_file)

    # 检查封面标题
    print("=" * 60)
    print("封面标题")
    print("=" * 60)
    for i, para in enumerate(doc.paragraphs[:10]):
        if para.text.strip():
            print(f"段落 {i}: {para.text[:50]}...")
            # 检查字体
            for run in para.runs:
                if run.text.strip():
                    font_name = utils.get_font_name(run)
                    font_size = utils.get_font_size(run)
                    print(f"  字体: {font_name}")
                    print(f"  字号: {font_size}")
                    break
            # 检查对齐
            align = utils.get_paragraph_alignment(para)
            print(f"  对齐: {align}")
            print()

    # 检查中英文摘要标题
    print("=" * 60)
    print("摘要标题")
    print("=" * 60)
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if text in ["摘要", "ABSTRACT", "关键词", "Keywords"]:
            print(f"段落 {i}: {text}")
            align = utils.get_paragraph_alignment(para)
            print(f"  对齐: {align}")
            for run in para.runs:
                if run.text.strip():
                    font_name = utils.get_font_name(run)
                    font_size = utils.get_font_size(run)
                    bold = utils.get_font_bold(run)
                    print(f"  字体: {font_name}, 字号: {font_size}, 加粗: {bold}")
                    break
            print()

    # 检查关键词行
    print("=" * 60)
    print("关键词段落")
    print("=" * 60)
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if "关键词" in text and "：" in text:
            print(f"段落 {i}: {text[:60]}...")
            # 检查是否有分号
            if "；" in text:
                print("  ❌ 仍包含中文分号")
            if ";" in text:
                print("  ❌ 仍包含英文分号")
            if "，" in text:
                print("  ✓ 包含中文逗号")
            print()

    # 检查章节标题
    print("=" * 60)
    print("章节标题")
    print("=" * 60)
    chapter_count = 0
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if text.startswith("一、") or text.startswith("二、") or text.startswith("三、") or \
           text.startswith("四、") or text.startswith("五、") or text.startswith("六、") or \
           text.startswith("七、") or text.startswith("八、") or text.startswith("九、") or \
           text.startswith("十、"):
            print(f"段落 {i}: {text[:40]}...")
            align = utils.get_paragraph_alignment(para)
            print(f"  对齐: {align}")
            for run in para.runs:
                if run.text.strip():
                    font_name = utils.get_font_name(run)
                    font_size = utils.get_font_size(run)
                    bold = utils.get_font_bold(run)
                    print(f"  字体: {font_name}, 字号: {font_size}, 加粗: {bold}")
                    break
            print()
            chapter_count += 1
            if chapter_count >= 5:
                break

    # 检查正文段落格式
    print("=" * 60)
    print("正文段落示例")
    print("=" * 60)
    for i, para in enumerate(doc.paragraphs[20:40]):
        text = para.text.strip()
        if len(text) > 50:
            print(f"段落 {i+20}: {text[:50]}...")
            align = utils.get_paragraph_alignment(para)
            indent = utils.get_first_line_indent(para)
            line_spacing = utils.get_line_spacing(para)
            print(f"  对齐: {align}")
            print(f"  首行缩进: {indent}")
            print(f"  行距: {line_spacing}")
            print()
            break

    return 0


def run_fix_mode(input_file: str, rules_path: str, args):
    """修复模式：自动修复格式问题"""
    from emba_checker.docx_autofixer import auto_fix

    print("\n开始自动修复...\n")

    output_path, report = auto_fix(
        input_file,
        rules_path,
        output_path=args.output,
        backup=not args.no_backup,
        verbose=args.verbose
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

    # 生成修复报告文件
    report_path = output_path.replace(".docx", "_修复报告.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report.to_string())

    print(f"\n修复报告: {report_path}")

    return 0


def main():
    """主入口"""
    args = parse_args()
    
    # 自动查找docx文件
    docx_files = glob.glob('data/*.docx')
    
    # 显示帮助信息
    if args.input_file is None and not docx_files:
        print("""
EMBA 论文格式自动修复工具

使用方法:
  python run_autofix.py input.docx                    # 修复文档
  python run_autofix.py input.docx --check            # 只检查不修复
  python run_autofix.py input.docx --inspect          # 检查文档实际格式
  python run_autofix.py input.docx --diff             # 对比格式差异
  python run_autofix.py input.docx --diff --original original.docx  # 指定原始文件对比
  python run_autofix.py input.docx -o ./output        # 指定输出目录
  python run_autofix.py input.docx --no-backup        # 不备份原文件
  python run_autofix.py input.docx -v                  # 显示详细日志
        """)
        return 0
    
    # 使用输入参数或自动查找
    if args.input_file:
        input_file = args.input_file
    elif docx_files:
        input_file = docx_files[0]
        print(f"自动选择文件: {input_file}")
    else:
        print("错误: 未找到输入文件", file=sys.stderr)
        return 1
    
    # 验证输入文件
    if not os.path.exists(input_file):
        print(f"错误: 输入文件不存在: {input_file}", file=sys.stderr)
        return 1
    
    # 验证文件扩展名
    if not input_file.lower().endswith('.docx'):
        print(f"错误: 输入文件必须是 .docx 格式", file=sys.stderr)
        return 1
    
    # 获取规则文件路径
    rules_path = args.rules if args.rules else os.path.join(BASE_DIR, 'emba_checker', 'rules_registry.json')
    if not os.path.exists(rules_path):
        print(f"错误: 规则文件不存在: {rules_path}", file=sys.stderr)
        return 1
    
    # 打印配置信息
    print("=" * 60)
    print("EMBA 论文格式自动修复工具")
    print("=" * 60)
    print(f"论文文件: {input_file}")
    print(f"规则文件: {rules_path}")
    print(f"备份原文件: {'否' if args.no_backup else '是'}")
    if args.output:
        print(f"输出目录: {args.output}")

    # 确定运行模式
    if args.diff:
        mode = "对比模式（对比原始和修复文档格式差异）"
    elif args.inspect:
        mode = "检查模式（检查文档实际格式）"
    elif args.check:
        mode = "检查模式（只检查不修复）"
    else:
        mode = "修复模式"
    print(f"运行模式: {mode}")
    print("-" * 60)

    try:
        # 对比模式
        if args.diff:
            return run_diff_mode(input_file, args.original)
        # 检查模式（检查文档实际格式）
        elif args.inspect:
            return run_inspect_mode(input_file)
        # 检查模式（验证格式问题）
        elif args.check:
            return run_check_mode(input_file, rules_path, args.verbose)
        else:
            # 修复模式 - 调用自动修复
            return run_fix_mode(input_file, rules_path, args)
        
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
