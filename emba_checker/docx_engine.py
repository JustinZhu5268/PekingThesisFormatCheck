# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - Python 确定性检查引擎
实现 6 个 Group 的分组遍历逻辑
"""

import os
import sys
from typing import List, Dict, Any, Optional, Callable
from docx.document import Document
from docx.table import Table

# 添加项目根目录到路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)


class DocxEngine:
    """
    Python 确定性检查引擎
    
    负责：
    1. 6 个 Group 的分组遍历
    - Group 1: Global (全局属性) — 不遍历段落
    - Group 1B: HeaderFooter (页眉页脚) — 遍历 sections 的 header/footer
    - Group 2: Paragraphs (段落与文本) — 核心遍历，覆盖最多规则
    - Group 3: Tables & Figures (图表) — 遍历表格和内联图
    - Group 4: Footnotes (脚注) — 通过 XML 安全读取
    - Group 5: References (参考文献) — 定位后集中处理
    - Group 6: Cross-references (交叉引用) — 全局扫描
    
    2. 将遍历与执行器串联
    3. 收集 Issue
    """
    
    # Group 定义
    GROUPS = {
        "Group1_Global": {
            "name": "全局属性",
            "traverse": "sections",
            "description": "纸张A4、页边距、页眉页脚距边界、装订线",
        },
        "Group1_HeaderFooter": {
            "name": "页眉页脚",
            "traverse": "header_footer",
            "description": "页眉字体、页眉内容、页码字体、页码位置、奇偶页设置",
        },
        "Group2_Paragraphs": {
            "name": "段落与文本",
            "traverse": "paragraphs",
            "description": "封面格式、版权声明、摘要格式、目录格式、正文标题、正文段落、标点等",
        },
        "Group3_Figures": {
            "name": "图片",
            "traverse": "figures",
            "description": "图片编号格式、题注位置、图片字体",
        },
        "Group3_Tables": {
            "name": "表格",
            "traverse": "tables",
            "description": "表格编号格式、表格字体、资料来源、续表",
        },
        "Group4_Footnotes": {
            "name": "脚注",
            "traverse": "footnotes",
            "description": "脚注字体、缩进、行距、序号、网址标注",
        },
        "Group5_References": {
            "name": "参考文献",
            "traverse": "references",
            "description": "悬挂缩进、无序号、英文标点、排序、去重、著者格式",
        },
        "Group6_CrossRef": {
            "name": "交叉引用",
            "traverse": "cross_ref",
            "description": "图表编号与正文引用对应、参考文献列表与正文引用对应",
        },
    }
    
    def __init__(self, doc: Document, rules: List[Dict], zone_map: Dict[int, str], 
                 progress_callback: Optional[Callable] = None):
        self.doc = doc
        self.rules = rules
        self.zone_map = zone_map
        self.progress_callback = progress_callback
        self.issues: List[Any] = []
        self.execution_log: List[str] = []
        
        # 按 Group 分组规则
        self.rules_by_group = self._group_rules()
    
    def _group_rules(self) -> Dict[str, List[Dict]]:
        """按 Group 分组规则"""
        grouped = {group: [] for group in self.GROUPS.keys()}
        
        for rule in self.rules:
            group = rule.get("target_group", "Group2_Paragraphs")
            if group in grouped:
                grouped[group].append(rule)
            else:
                grouped["Group2_Paragraphs"].append(rule)
        
        return grouped
    
    def _report_progress(self, group: str, message: str, current: int = None, total: int = None):
        """报告进度"""
        if self.progress_callback:
            self.progress_callback(group, message, current, total)
        self.execution_log.append(f"[{group}] {message}")
    
    def run_all(self) -> List[Any]:
        """运行所有 Group 的检查"""
        self.issues = []
        
        # 按顺序执行每个 Group
        group_order = [
            ("Group1_Global", self._check_global),
            ("Group1_HeaderFooter", self._check_header_footer),
            ("Group2_Paragraphs", self._check_paragraphs),
            ("Group3_Figures", self._check_figures),
            ("Group3_Tables", self._check_tables),
            ("Group4_Footnotes", self._check_footnotes),
            ("Group5_References", self._check_references),
            ("Group6_CrossRef", self._check_cross_ref),
        ]
        
        for group_name, check_func in group_order:
            rules = self.rules_by_group.get(group_name, [])
            if not rules:
                self._report_progress(group_name, f"跳过 (无规则)", 0, 0)
                continue
            
            self._report_progress(group_name, f"开始检查 {len(rules)} 条规则", 0, len(rules))
            
            try:
                group_issues = check_func(rules)
                self.issues.extend(group_issues)
                self._report_progress(group_name, f"完成，发现 {len(group_issues)} 个问题", len(rules), len(rules))
            except Exception as e:
                self._report_progress(group_name, f"执行出错: {str(e)}", 0, 0)
        
        return self.issues
    
    def _check_global(self, rules: List[Dict]) -> List[Any]:
        """Group 1: 全局属性检查"""
        issues = []
        
        # 导入执行器
        from emba_checker.executors.global_property_executor import GlobalPropertyExecutor
        
        executor = GlobalPropertyExecutor(self.doc, rules, self.zone_map)
        
        for rule in rules:
            if not rule.get("enabled", True):
                continue
            
            try:
                issue = executor.check(rule)
                if issue:
                    issues.append(issue)
            except Exception as e:
                issues.append(self._create_error_issue(rule, str(e)))
        
        return issues
    
    def _check_header_footer(self, rules: List[Dict]) -> List[Any]:
        """Group 1B: 页眉页脚检查"""
        issues = []
        
        # TODO: 使用 lxml 读取页眉页脚 XML
        # 当前先跳过，因为 python-docx 对页眉支持有限
        
        self._report_progress("Group1_HeaderFooter", "页眉页脚检查（待实现）", 0, 0)
        
        return issues
    
    def _check_paragraphs(self, rules: List[Dict]) -> List[Any]:
        """Group 2: 段落检查"""
        issues = []
        
        # 导入执行器
        from emba_checker.rule_engine import RuleEngine
        
        engine = RuleEngine(self.doc, rules, self.zone_map)
        
        try:
            group_issues = engine.run_all()
            issues.extend(group_issues)
        except Exception as e:
            self._report_progress("Group2_Paragraphs", f"执行出错: {str(e)}", 0, 0)
        
        return issues
    
    def _check_figures(self, rules: List[Dict]) -> List[Any]:
        """Group 3: 图片检查"""
        issues = []
        
        # 遍历文档中的内联图形
        for i, shape in enumerate(self.doc.inline_shapes):
            # TODO: 检查图片属性（宽度、高度、格式等）
            pass
        
        self._report_progress("Group3_Figures", f"检查了 {len(self.doc.inline_shapes)} 个内联图形", 0, 0)
        
        return issues
    
    def _check_tables(self, rules: List[Dict]) -> List[Any]:
        """Group 3: 表格检查"""
        issues = []
        
        # 遍历文档中的表格
        for table_idx, table in enumerate(self.doc.tables):
            table_issues = self._check_single_table(table, table_idx, rules)
            issues.extend(table_issues)
        
        self._report_progress("Group3_Tables", f"检查了 {len(self.doc.tables)} 个表格", 0, 0)
        
        return issues
    
    def _check_single_table(self, table: Table, table_idx: int, rules: List[Dict]) -> List[Any]:
        """检查单个表格"""
        issues = []
        
        # TODO: 根据规则检查表格样式
        # - 表格字体
        # - 表格对齐
        # - 单元格边距
        # - 资料来源位置
        
        return issues
    
    def _check_footnotes(self, rules: List[Dict]) -> List[Any]:
        """Group 4: 脚注检查"""
        issues = []
        
        # TODO: 使用 lxml 读取脚注 XML
        # python-docx 没有原生 footnotes API，需要通过 lxml 读取
        
        self._report_progress("Group4_Footnotes", "脚注检查（待实现）", 0, 0)
        
        return issues
    
    def _check_references(self, rules: List[Dict]) -> List[Any]:
        """Group 5: 参考文献检查"""
        issues = []
        
        # 获取参考文献区域的段落
        ref_paragraphs = []
        for i, para in enumerate(self.doc.paragraphs):
            zone = self.zone_map.get(i, "unknown")
            if zone == "references":
                ref_paragraphs.append((i, para))
        
        # 导入执行器
        from emba_checker.rule_engine import RuleEngine
        
        engine = RuleEngine(self.doc, rules, self.zone_map)
        
        try:
            # 只检查参考文献相关的规则
            ref_rules = [r for r in rules if "reference" in r.get("target_zone", [])]
            if ref_rules:
                group_issues = engine.run_all()
                issues.extend(group_issues)
        except Exception as e:
            self._report_progress("Group5_References", f"执行出错: {str(e)}", 0, 0)
        
        self._report_progress("Group5_References", f"检查了 {len(ref_paragraphs)} 个参考文献条目", 0, 0)
        
        return issues
    
    def _check_cross_ref(self, rules: List[Dict]) -> List[Any]:
        """Group 6: 交叉引用检查"""
        issues = []
        
        # 导入执行器
        from emba_checker.executors.cross_reference_executor import CrossReferenceExecutor
        
        executor = CrossReferenceExecutor(self.doc, rules, self.zone_map)
        
        for rule in rules:
            if not rule.get("enabled", True):
                continue
            
            try:
                issue = executor.check(rule)
                if issue:
                    issues.append(issue)
            except Exception as e:
                issues.append(self._create_error_issue(rule, str(e)))
        
        return issues
    
    def _create_error_issue(self, rule: Dict, error_msg: str) -> Any:
        """创建错误 Issue"""
        from emba_checker.base_executor import CheckIssue
        
        return CheckIssue(
            rule_id=rule.get("rule_id", "unknown"),
            check_type=rule.get("check_type", "unknown"),
            result="error",
            message=f"检查执行出错: {error_msg}",
            severity="error"
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """获取检查摘要"""
        summary = {
            "total_issues": len(self.issues),
            "by_severity": {
                "error": 0,
                "warning": 0,
                "info": 0,
            },
            "by_group": {},
        }
        
        for issue in self.issues:
            severity = getattr(issue, 'severity', 'info')
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
        
        for group, rules in self.rules_by_group.items():
            group_issues = [i for i in self.issues if getattr(i, 'rule_id', '').startswith(group.split('_')[0])]
            summary["by_group"][group] = len(group_issues)
        
        return summary


def run_docx_engine(doc: Document, rules: List[Dict], zone_map: Dict[int, str],
                    progress_callback: Optional[Callable] = None) -> List[Any]:
    """
    运行 Python 引擎的便捷函数
    
    Args:
        doc: Document 对象
        rules: 规则列表
        zone_map: 区域映射
        progress_callback: 进度回调函数
        
    Returns:
        List[Any]: 检查问题列表
    """
    engine = DocxEngine(doc, rules, zone_map, progress_callback)
    return engine.run_all()
