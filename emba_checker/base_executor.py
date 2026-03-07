# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 执行器基类
定义所有执行器的公共接口
"""

import json
import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CheckType(Enum):
    """检查类型枚举"""
    PARAGRAPH_STYLE = "paragraph_style"
    GLOBAL_PROPERTY = "global_property"
    REGEX_MATCH = "regex_match"
    COUNT_CHECK = "count_check"
    CROSS_REFERENCE = "cross_reference"
    TEXT_MATCH = "text_match"
    FORBIDDEN_WORDS = "forbidden_words"
    AI_SEMANTIC = "ai_semantic"
    SKIP = "skip"


class CheckResult(Enum):
    """检查结果枚举"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"
    ERROR = "error"


@dataclass
class CheckIssue:
    """检查问题记录"""
    rule_id: str
    check_type: str
    result: str
    message: str
    location: Optional[Dict[str, Any]] = None
    severity: str = "error"  # error, warning, info
    
    def to_dict(self) -> Dict:
        return {
            "rule_id": self.rule_id,
            "check_type": self.check_type,
            "result": self.result,
            "message": self.message,
            "location": self.location,
            "severity": self.severity,
        }


@dataclass
class CheckReport:
    """检查报告"""
    total_rules: int
    passed: int
    failed: int
    warnings: int
    skipped: int
    errors: int
    issues: List[CheckIssue]
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return {
            "total_rules": self.total_rules,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "skipped": self.skipped,
            "errors": self.errors,
            "issues": [i.to_dict() for i in self.issues],
            "details": self.details,
        }
    
    def summary(self) -> str:
        lines = []
        lines.append("=" * 50)
        lines.append("检查报告摘要")
        lines.append("=" * 50)
        lines.append(f"总规则数: {self.total_rules}")
        lines.append(f"通过: {self.passed}")
        lines.append(f"失败: {self.failed}")
        lines.append(f"警告: {self.warnings}")
        lines.append(f"跳过: {self.skipped}")
        lines.append(f"错误: {self.errors}")
        lines.append("=" * 50)
        
        if self.issues:
            lines.append("\n问题详情:")
            for issue in self.issues:
                lines.append(f"  [{issue.result.upper()}] {issue.rule_id}: {issue.message}")
        
        return "\n".join(lines)


class BaseExecutor(ABC):
    """执行器基类"""
    
    def __init__(self, doc, rules: List[Dict], zone_map: Dict[int, str]):
        self.doc = doc
        self.rules = rules
        self.zone_map = zone_map
        self.issues: List[CheckIssue] = []
        
        # 加载规则库
        self._load_rules()
    
    def _load_rules(self):
        """加载规则库"""
        rules_path = os.path.join(
            os.path.dirname(__file__),
            "rules_registry.json"
        )
        
        if not os.path.exists(rules_path):
            self.all_rules = []
            return
        
        with open(rules_path, 'r', encoding='utf-8') as f:
            self.all_rules = json.load(f)
    
    def _get_rule_by_id(self, rule_id: str) -> Optional[Dict]:
        """根据 rule_id 获取规则"""
        for rule in self.all_rules:
            if rule.get("rule_id") == rule_id:
                return rule
        return None
    
    def _get_paragraphs_in_zones(self, zones: List[str]) -> List[Tuple[int, Any]]:
        """获取指定区域的所有段落"""
        result = []
        for i, para in enumerate(self.doc.paragraphs):
            zone = self.zone_map.get(i, "unknown")
            if zone in zones:
                result.append((i, para))
        return result
    
    def _get_text_in_zones(self, zones: List[str]) -> str:
        """获取指定区域的所有文本"""
        texts = []
        for i, para in enumerate(self.doc.paragraphs):
            zone = self.zone_map.get(i, "unknown")
            if zone in zones:
                texts.append(para.text)
        return "\n".join(texts)
    
    @abstractmethod
    def check(self, rule: Dict) -> CheckIssue:
        """
        执行检查
        
        Args:
            rule: 规则字典
            
        Returns:
            CheckIssue: 检查结果
        """
        pass
    
    def execute(self, rule_ids: List[str] = None) -> List[CheckIssue]:
        """
        执行检查
        
        Args:
            rule_ids: 要检查的规则ID列表，None表示检查所有
            
        Returns:
            List[CheckIssue]: 检查问题列表
        """
        self.issues = []
        
        # 筛选要检查的规则
        rules_to_check = []
        for rule in self.rules:
            if rule_ids is None or rule.get("rule_id") in rule_ids:
                if rule.get("enabled", True):
                    rules_to_check.append(rule)
        
        # 执行检查
        for rule in rules_to_check:
            try:
                issue = self.check(rule)
                if issue:
                    self.issues.append(issue)
            except Exception as e:
                # 记录错误
                issue = CheckIssue(
                    rule_id=rule.get("rule_id", "unknown"),
                    check_type=rule.get("check_type", "unknown"),
                    result=CheckResult.ERROR.value,
                    message=f"检查执行出错: {str(e)}",
                    severity="error"
                )
                self.issues.append(issue)
        
        return self.issues
    
    def generate_report(self) -> CheckReport:
        """生成检查报告"""
        passed = sum(1 for i in self.issues if i.result == CheckResult.PASS.value)
        failed = sum(1 for i in self.issues if i.result == CheckResult.FAIL.value)
        warnings = sum(1 for i in self.issues if i.result == CheckResult.WARNING.value)
        skipped = sum(1 for i in self.issues if i.result == CheckResult.SKIP.value)
        errors = sum(1 for i in self.issues if i.result == CheckResult.ERROR.value)
        
        return CheckReport(
            total_rules=len(self.rules),
            passed=passed,
            failed=failed,
            warnings=warnings,
            skipped=skipped,
            errors=errors,
            issues=self.issues,
            details={}
        )


class ExecutorFactory:
    """执行器工厂"""
    
    @staticmethod
    def create(check_type: str, doc, rules: List[Dict], zone_map: Dict[int, str]) -> BaseExecutor:
        """
        创建执行器
        
        Args:
            check_type: 检查类型
            doc: Document 对象
            rules: 规则列表
            zone_map: 区域映射
            
        Returns:
            BaseExecutor: 执行器实例
        """
        # 延迟导入避免循环依赖
        from .executors.paragraph_style_executor import ParagraphStyleExecutor
        from .executors.global_property_executor import GlobalPropertyExecutor
        from .executors.regex_match_executor import RegexMatchExecutor
        from .executors.count_check_executor import CountCheckExecutor
        from .executors.cross_reference_executor import CrossReferenceExecutor
        from .executors.text_match_executor import TextMatchExecutor
        from .executors.forbidden_words_executor import ForbiddenWordsExecutor
        from .executors.ai_semantic_executor import AISemanticExecutor
        
        executor_map = {
            CheckType.PARAGRAPH_STYLE.value: ParagraphStyleExecutor,
            CheckType.GLOBAL_PROPERTY.value: GlobalPropertyExecutor,
            CheckType.REGEX_MATCH.value: RegexMatchExecutor,
            CheckType.COUNT_CHECK.value: CountCheckExecutor,
            CheckType.CROSS_REFERENCE.value: CrossReferenceExecutor,
            CheckType.TEXT_MATCH.value: TextMatchExecutor,
            CheckType.FORBIDDEN_WORDS.value: ForbiddenWordsExecutor,
            CheckType.AI_SEMANTIC.value: AISemanticExecutor,
            "skip": None,  # 跳过
        }
        
        executor_class = executor_map.get(check_type)
        
        if executor_class is None:
            # 返回一个空的执行器
            class DummyExecutor(BaseExecutor):
                def check(self, rule):
                    return CheckIssue(
                        rule_id=rule.get("rule_id", "unknown"),
                        check_type=rule.get("check_type", "unknown"),
                        result=CheckResult.SKIP.value,
                        message=f"未实现的检查类型: {check_type}",
                        severity="info"
                    )
            return DummyExecutor(doc, rules, zone_map)
        
        return executor_class(doc, rules, zone_map)
