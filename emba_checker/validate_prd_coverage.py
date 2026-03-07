# -*- coding: utf-8 -*-
"""
validate_prd_coverage.py - PRD功能需求覆盖率验证脚本

用法:
    python validate_prd_coverage.py

扫描所有测试文件，提取 @pytest.mark.prd("FR-xxx") 标记，
并与 PRD 需求列表比对，输出未覆盖项。
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# PRD功能需求定义
PRD_REQUIREMENTS = {
    # 红线要求 (Req)
    "REQ-1": "基于MD清单生成自动检查工具",
    "REQ-2": "黄色高亮违规处+旁侧红色加粗标注修改建议",
    "REQ-3": "规则库先行，禁止业务代码硬编码if-else",
    "REQ-4": "同类规则分组遍历，最少遍历次数",
    "REQ-5": "自动化双向核对：MD↔规则库100%覆盖",
    "REQ-6": "极简GUI+Claude Sonnet 4.5 API双擎独立运行",
    "REQ-7": "零风险容忍：绝对禁止XML写入批注，安全降级链",

    # 检查类型 (FR-CHECK-xxx)
    "FR-CHECK-01": "paragraph_style - 段落样式检查",
    "FR-CHECK-02": "global_property - 全局/节属性检查",
    "FR-CHECK-03": "regex_match - 正则匹配检查",
    "FR-CHECK-04": "count_check - 计数/统计检查",
    "FR-CHECK-05": "cross_reference - 交叉引用检查",
    "FR-CHECK-06": "text_match - 文本精确匹配/包含检查",
    "FR-CHECK-07": "forbidden_words - 禁用词/词库检查",
    "FR-CHECK-08": "ai_semantic - Claude语义检查",

    # 区域识别 (FR-ZONE-xxx)
    "FR-ZONE-01": "cover - 封面区域检测",
    "FR-ZONE-02": "copyright - 版权声明区域",
    "FR-ZONE-03": "declaration - 原创性声明区域",
    "FR-ZONE-04": "abstract_cn - 中文摘要区域",
    "FR-ZONE-05": "abstract_en - 英文摘要区域",
    "FR-ZONE-06": "toc - 目录区域",
    "FR-ZONE-07": "body_chapter - 正文章节区域",
    "FR-ZONE-08": "references - 参考文献区域",
    "FR-ZONE-09": "appendix - 附录区域",
    "FR-ZONE-10": "acknowledgment - 致谢区域",

    # 分组遍历 (FR-GROUP-xxx)
    "FR-GROUP-01": "Group1_Global - 全局属性遍历",
    "FR-GROUP-02": "Group1B_HeaderFooter - 页眉页脚遍历",
    "FR-GROUP-03": "Group2_Paragraphs - 段落与文本遍历",
    "FR-GROUP-04": "Group3_Figures - 图表遍历",
    "FR-GROUP-05": "Group4_Footnotes - 脚注遍历",
    "FR-GROUP-06": "Group5_References - 参考文献遍历",
    "FR-GROUP-07": "Group6_CrossRefs - 交叉引用遍历",

    # 引擎 (FR-ENGINE-xxx)
    "FR-ENGINE-01": "DocxEngine - Python确定性检查引擎",
    "FR-ENGINE-02": "ClaudeEngine - Claude语义引擎",
    "FR-ENGINE-03": "双擎独立运行机制",
    "FR-ENGINE-04": "结果合并去重",

    # 标注 (FR-ANNOTATE-xxx)
    "FR-ANNOTATE-01": "黄色高亮违规处",
    "FR-ANNOTATE-02": "独立段落标注(优先)",
    "FR-ANNOTATE-03": "段落末尾追加Run(降级1)",
    "FR-ANNOTATE-04": "仅记录到报告(降级2)",
    "FR-ANNOTATE-05": "文件安全保障-先复制后操作",

    # GUI (FR-GUI-xxx)
    "FR-GUI-01": "文件选择功能",
    "FR-GUI-02": "API Key输入",
    "FR-GUI-03": "检查级别选择",
    "FR-GUI-04": "进度条显示",
    "FR-GUI-05": "结果摘要展示",
    "FR-GUI-06": "日志显示",
    "FR-GUI-07": "打开docx文件",
    "FR-GUI-08": "打开报告文件",

    # 规则库 (FR-RULE-xxx)
    "FR-RULE-01": "MD清单解析器",
    "FR-RULE-02": "规则库生成器",
    "FR-RULE-03": "手动覆盖配置",
    "FR-RULE-04": "规则覆盖验证",
    "FR-RULE-05": "164条规则映射",

    # 工具函数 (FR-UTIL-xxx)
    "FR-UTIL-01": "EMU单位换算",
    "FR-UTIL-02": "中文字符计数",
    "FR-UTIL-03": "英文字符计数",
    "FR-UTIL-04": "正则匹配",
    "FR-UTIL-05": "XML安全读取",
    "FR-UTIL-06": "字体属性获取",
    "FR-UTIL-07": "段落属性获取",
    "FR-UTIL-08": "页面设置获取",

    # 测试 (FR-TEST-xxx)
    "FR-TEST-01": "单元测试-工具函数",
    "FR-TEST-02": "单元测试-区域检测",
    "FR-TEST-03": "单元测试-规则解析",
    "FR-TEST-04": "单元测试-执行器",
    "FR-TEST-05": "集成测试-引擎管道",
    "FR-TEST-06": "集成测试-双擎协作",
    "FR-TEST-07": "E2E测试-完整流程",
    "FR-TEST-08": "E2E测试-GUI交互",
}


def find_prd_markers_in_file(file_path: Path) -> Set[str]:
    """在单个测试文件中查找所有PRD标记"""
    markers = set()
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception:
        return markers
    
    # 匹配 @pytest.mark.prd("FR-xxx") 或 @pytest.mark.prd('FR-xxx')
    pattern = r'@pytest\.mark\.prd\(["\']([A-Z0-9\-]+)["\']\)'
    
    for match in re.finditer(pattern, content):
        markers.add(match.group(1))
    
    return markers


def scan_test_directory(test_dir: str) -> Tuple[Set[str], Dict[str, List[str]]]:
    """扫描测试目录，找出所有PRD标记"""
    all_markers = set()
    file_markers = {}
    
    test_path = Path(test_dir)
    if not test_path.exists():
        return all_markers, file_markers
    
    # 递归扫描所有Python测试文件
    for py_file in test_path.rglob("test_*.py"):
        markers = find_prd_markers_in_file(py_file)
        if markers:
            rel_path = str(py_file.relative_to(test_path.parent))
            file_markers[rel_path] = list(markers)
            all_markers.update(markers)
    
    return all_markers, file_markers


def generate_coverage_report(
    prd_requirements: Dict[str, str],
    found_markers: Set[str]
) -> str:
    """生成覆盖率报告"""
    lines = []
    lines.append("=" * 70)
    lines.append("PRD 功能需求覆盖率报告")
    lines.append("=" * 70)
    lines.append("")
    
    # 统计
    total_req = len(prd_requirements)
    covered_req = len(found_markers)
    coverage_pct = (covered_req / total_req * 100) if total_req > 0 else 0
    
    lines.append(f"PRD需求总数: {total_req}")
    lines.append(f"已覆盖需求: {covered_req}")
    lines.append(f"覆盖率: {coverage_pct:.1f}%")
    lines.append("")
    
    # 未覆盖的需求
    uncovered = set(prd_requirements.keys()) - found_markers
    
    if uncovered:
        lines.append("-" * 70)
        lines.append("未覆盖的需求 (需要添加测试):")
        lines.append("-" * 70)
        for req_id in sorted(uncovered):
            lines.append(f"  [{req_id}] {prd_requirements[req_id]}")
        lines.append("")
    
    # 已覆盖的需求
    covered = set(prd_requirements.keys()) & found_markers
    if covered:
        lines.append("-" * 70)
        lines.append("已覆盖的需求:")
        lines.append("-" * 70)
        for req_id in sorted(covered):
            lines.append(f"  [✓] [{req_id}] {prd_requirements[req_id]}")
        lines.append("")
    
    # 按类别分组显示
    categories = {
        "红线要求": ["REQ-1", "REQ-2", "REQ-3", "REQ-4", "REQ-5", "REQ-6", "REQ-7"],
        "检查类型": [k for k in prd_requirements.keys() if k.startswith("FR-CHECK")],
        "区域识别": [k for k in prd_requirements.keys() if k.startswith("FR-ZONE")],
        "分组遍历": [k for k in prd_requirements.keys() if k.startswith("FR-GROUP")],
        "引擎": [k for k in prd_requirements.keys() if k.startswith("FR-ENGINE")],
        "标注": [k for k in prd_requirements.keys() if k.startswith("FR-ANNOTATE")],
        "GUI": [k for k in prd_requirements.keys() if k.startswith("FR-GUI")],
        "规则库": [k for k in prd_requirements.keys() if k.startswith("FR-RULE")],
        "工具函数": [k for k in prd_requirements.keys() if k.startswith("FR-UTIL")],
        "测试": [k for k in prd_requirements.keys() if k.startswith("FR-TEST")],
    }
    
    lines.append("-" * 70)
    lines.append("按类别统计:")
    lines.append("-" * 70)
    
    for category, req_ids in categories.items():
        if req_ids:
            covered_in_cat = len([r for r in req_ids if r in found_markers])
            total_in_cat = len(req_ids)
            lines.append(f"  {category}: {covered_in_cat}/{total_in_cat}")
    
    lines.append("")
    lines.append("=" * 70)
    
    return "\n".join(lines)


def main():
    """主函数"""
    # 确定测试目录 - 修正路径计算
    script_dir = Path(__file__).parent  # emba_checker目录
    
    if len(sys.argv) > 1:
        test_dir = sys.argv[1]
    else:
        # 默认使用 tests 子目录
        test_dir = str(script_dir / "tests")
    
    print(f"扫描测试目录: {test_dir}")
    print()
    
    # 扫描测试文件
    found_markers, file_markers = scan_test_directory(test_dir)
    
    if not found_markers:
        print("警告: 未找到任何 @pytest.mark.prd 标记")
        print()
        print("请在测试文件中添加PRD标记，例如:")
        print('    @pytest.mark.prd("FR-CHECK-01")')
        print('    @pytest.mark.prd("FR-GUI-01")')
        print()
    
    # 显示每个文件的标记
    if file_markers:
        print("找到的PRD标记:")
        for file_path, markers in sorted(file_markers.items()):
            print(f"  {file_path}:")
            for m in sorted(markers):
                print(f"    - {m}")
        print()
    
    # 生成报告
    report = generate_coverage_report(PRD_REQUIREMENTS, found_markers)
    print(report)
    
    # 保存报告到文件
    report_path = Path(test_dir).parent / "prd_coverage_report.txt"
    report_path.write_text(report, encoding='utf-8')
    print(f"\n报告已保存到: {report_path}")
    
    # 返回退出码
    uncovered = set(PRD_REQUIREMENTS.keys()) - found_markers
    if uncovered:
        print(f"\n发现 {len(uncovered)} 个未覆盖的PRD需求，请添加相应测试!")
        return 1
    else:
        print("\n恭喜! 所有PRD需求都已覆盖测试!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
