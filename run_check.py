# -*- coding: utf-8 -*-
import sys
import io
import os
import glob
import shutil
from datetime import datetime

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, '.')

# 用glob获取docx文件
docx_files = glob.glob('data/*.docx')
if not docx_files:
    print('No docx file found in data/')
    sys.exit(1)

doc_path = docx_files[0]
print('Using file:', doc_path)

from emba_checker.main_engine import MainEngine
from emba_checker.safe_annotator import SafeAnnotator, generate_report as gen_report
from docx import Document

# 禁用 Claude
def progress(src, msg, cur=None, tot=None):
    print('[{}] {}'.format(src, msg))

# 使用 manual_overrides.json 作为规则文件
rules_path = 'emba_checker/rules_registry.json'
print('Using rules:', rules_path)

try:
    engine = MainEngine(doc_path, rules_path, None, progress)
    issues = engine.run(enable_claude=False)
    
    # 打印摘要
    summary = engine.get_summary()
    print('='*50)
    print('审查完成')
    print('='*50)
    print('发现问题总数:', summary['total_issues'])
    print('  错误:', summary['error_count'])
    print('  警告:', summary['warning_count'])
    print('  信息:', summary['info_count'])
    print('确定性检查:', summary['docx_engine_issues'], '条')
    print('AI 语义检查:', summary['claude_engine_issues'], '条')
    print('去重合并:', summary['deduplicated'], '条')
    print('总耗时:', round(summary['total_time'], 2), '秒')
    print('='*50)
    
    # 打印所有问题
    if issues:
        print('\n发现问题列表:')
        for i, issue in enumerate(issues):
            msg = issue.message[:80] if hasattr(issue, 'message') else str(issue)[:80]
            rule_id = issue.rule_id if hasattr(issue, 'rule_id') else 'N/A'
            severity = issue.severity if hasattr(issue, 'severity') else 'N/A'
            print('{}. [{}][{}] {}'.format(i+1, rule_id, severity, msg))
        
        # 生成输出文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        basename = os.path.splitext(os.path.basename(doc_path))[0]
        output_docx = f"{basename}_审查结果_{timestamp}.docx"
        output_report = f"{basename}_审查报告_{timestamp}.txt"
        
        print(f'\n正在生成标注文档: {output_docx}')
        shutil.copy2(doc_path, output_docx)
        doc = Document(output_docx)
        
        annotator = SafeAnnotator(doc, issues, output_docx)
        annotated, failed = annotator.annotate_all()
        doc.save(output_docx)
        
        print(f'  标注完成: {annotated} 个段落已标注, {failed} 个失败')
        
        # 生成报告
        print(f'正在生成报告: {output_report}')
        gen_report(doc_path, issues, output_report)
        
        print(f'\n输出文件:')
        print(f'  标注文档: {output_docx}')
        print(f'  审查报告: {output_report}')
    else:
        print('\n未发现问题!')
        
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()
