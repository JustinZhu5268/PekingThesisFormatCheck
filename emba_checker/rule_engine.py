# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 执行器统一入口
根据 check_type 创建对应的执行器并执行检查
"""

import os
import sys
from typing import List, Dict, Any, Optional
from docx.document import Document

# 添加项目根目录到路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)


# 动态导入
def _lazy_import():
    # 使用直接导入而非包导入
    import sys
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)
    
    from base_executor import BaseExecutor, CheckIssue, CheckResult
    
    # 直接导入各个执行器
    from executors.paragraph_style_executor import ParagraphStyleExecutor
    from executors.global_property_executor import GlobalPropertyExecutor
    from executors.regex_match_executor import RegexMatchExecutor
    from executors.count_check_executor import CountCheckExecutor
    from executors.cross_reference_executor import CrossReferenceExecutor
    from executors.text_match_executor import TextMatchExecutor
    from executors.forbidden_words_executor import ForbiddenWordsExecutor
    from executors.ai_semantic_executor import AISemanticExecutor
    
    return {
        "paragraph_style": ParagraphStyleExecutor,
        "global_property": GlobalPropertyExecutor,
        "regex_match": RegexMatchExecutor,
        "count_check": CountCheckExecutor,
        "cross_reference": CrossReferenceExecutor,
        "text_match": TextMatchExecutor,
        "forbidden_words": ForbiddenWordsExecutor,
        "ai_semantic": AISemanticExecutor,
        "CheckIssue": CheckIssue,
    }


class RuleEngine:
    """规则引擎 - 统一执行入口"""
    
    EXECUTOR_MAP = None  # 延迟初始化
    
    def __init__(self, doc: Document, rules: List[Dict], zone_map: Dict[int, str], api_key: Optional[str] = None):
        self.doc = doc
        self.rules = rules
        self.zone_map = zone_map
        self.api_key = api_key
        self.issues: List[Any] = []
        
        # 延迟加载执行器
        if RuleEngine.EXECUTOR_MAP is None:
            RuleEngine.EXECUTOR_MAP = _lazy_import()
    
    def _get_rules_by_check_type(self, check_type: str) -> List[Dict]:
        return [r for r in self.rules if r.get("check_type") == check_type]
    
    def _get_rules_by_group(self, group: str) -> List[Dict]:
        return [r for r in self.rules if r.get("target_group") == group]
    
    def run_all(self) -> List[Any]:
        self.issues = []
        CheckIssue = self.EXECUTOR_MAP["CheckIssue"]
        
        for rule in self.rules:
            if not rule.get("enabled", True):
                continue
            
            check_type = rule.get("check_type", "unknown")
            
            try:
                issue = self._run_single_rule(rule)
                if issue:
                    self.issues.append(issue)
            except Exception as e:
                self.issues.append(CheckIssue(
                    rule_id=rule.get("rule_id", "unknown"),
                    check_type=check_type,
                    result="error",
                    message=f"规则执行出错: {str(e)}",
                    severity="error"
                ))
        
        return self.issues
    
    def run_by_groups(self) -> Dict[str, List[Any]]:
        results = {}
        CheckIssue = self.EXECUTOR_MAP["CheckIssue"]
        
        group_order = [
            "Group1_Global",
            "Group1_HeaderFooter",
            "Group2_Paragraphs",
            "Group3_Figures",
            "Group3_Tables",
            "Group4_Footnotes",
            "Group5_References",
            "Group6_CrossRef",
        ]
        
        for group in group_order:
            rules = self._get_rules_by_group(group)
            if not rules:
                continue
            
            group_issues = []
            for rule in rules:
                if not rule.get("enabled", True):
                    continue
                
                try:
                    issue = self._run_single_rule(rule)
                    if issue:
                        group_issues.append(issue)
                except Exception as e:
                    group_issues.append(CheckIssue(
                        rule_id=rule.get("rule_id", "unknown"),
                        check_type=rule.get("check_type", "unknown"),
                        result="error",
                        message=f"规则执行出错: {str(e)}",
                        severity="error"
                    ))
            
            results[group] = group_issues
            self.issues.extend(group_issues)
        
        return results
    
    def _run_single_rule(self, rule: Dict) -> Optional[Any]:
        check_type = rule.get("check_type", "unknown")
        CheckIssue = self.EXECUTOR_MAP["CheckIssue"]
        
        if check_type == "skip":
            return CheckIssue(
                rule_id=rule.get("rule_id", "unknown"),
                check_type="skip",
                result="skip",
                message="规则已跳过",
                severity="info"
            )
        
        executor_class = self.EXECUTOR_MAP.get(check_type)
        
        if executor_class is None:
            return CheckIssue(
                rule_id=rule.get("rule_id", "unknown"),
                check_type=check_type,
                result="skip",
                message=f"未知的检查类型: {check_type}",
                severity="info"
            )
        
        if check_type == "ai_semantic":
            executor = executor_class(self.doc, self.rules, self.zone_map, self.api_key)
        else:
            executor = executor_class(self.doc, self.rules, self.zone_map)
        
        return executor.check(rule)
    
    def get_issue_summary(self) -> Dict[str, Any]:
        summary = {
            "total": len(self.issues),
            "by_severity": {
                "error": 0,
                "warning": 0,
                "info": 0,
            },
            "by_check_type": {},
            "by_rule_id": {},
        }
        
        for issue in self.issues:
            severity = getattr(issue, 'severity', 'info')
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            
            ct = getattr(issue, 'check_type', 'unknown')
            summary["by_check_type"][ct] = summary["by_check_type"].get(ct, 0) + 1
            
            rid = getattr(issue, 'rule_id', 'unknown')
            summary["by_rule_id"][rid] = summary["by_rule_id"].get(rid, 0) + 1
        
        return summary


def run_check(doc: Document, rules: List[Dict], zone_map: Dict[int, str], 
              api_key: Optional[str] = None) -> List[Any]:
    """运行规则检查的便捷函数"""
    engine = RuleEngine(doc, rules, zone_map, api_key)
    return engine.run_all()
