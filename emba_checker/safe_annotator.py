# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 安全标注模块
实现三级降级链：独立段落标注 → 末尾追加 → 仅记录报告
"""

import os
import sys
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

# 添加项目根目录到路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from docx.shared import Pt, RGBColor
from docx.enum.text import WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph


class SafeAnnotator:
    """
    安全标注模块
    
    实现三级降级链：
    1. 优先：独立段落标注（推荐）
    2. 降级1：段落末尾追加 Run
    3. 降级2：仅记录到报告文件
    """
    
    # 标注样式
    ANNOTATION_FONT_COLOR = RGBColor(255, 0, 0)  # 红色
    ANNOTATION_FONT_SIZE = Pt(9)  # 小五号
    ANNOTATION_FONT_BOLD = True
    
    # 高亮颜色
    HIGHLIGHT_COLOR = WD_COLOR_INDEX.YELLOW  # 黄色
    
    def __init__(self, doc, issues: List[Any], output_path: Optional[str] = None):
        self.doc = doc
        self.issues = issues
        self.output_path = output_path
        self.annotated_count = 0
        self.failed_count = 0
        self.annotation_log: List[str] = []
    
    def annotate_all(self) -> Tuple[int, int]:
        """
        对所有 Issue 进行标注
        
        Returns:
            (annotated_count, failed_count)
        """
        # 1. 按段落分组 Issue
        issues_by_para = self._group_issues_by_paragraph()
        
        # 2. 逐段落应用标注
        for para_index, para_issues in issues_by_para.items():
            # 跳过没有段落索引的问题（这些是全局性问题，如页面设置等）
            if para_index is None:
                self.annotation_log.append(f"全局性问题: {len(para_issues)} 个问题无法定位到具体段落")
                continue
            
            try:
                self._annotate_paragraph(para_index, para_issues)
                self.annotated_count += 1
            except Exception as e:
                self.failed_count += 1
                self.annotation_log.append(f"段落 {para_index} 标注失败: {str(e)}")
        
        return self.annotated_count, self.failed_count
    
    def _group_issues_by_paragraph(self) -> Dict[int, List[Any]]:
        """按段落索引分组 Issue"""
        grouped = defaultdict(list)
        
        for issue in self.issues:
            # 获取段落索引
            para_indices = []
            
            if hasattr(issue, 'location') and issue.location:
                # 优先使用 paragraph_index
                para_index = issue.location.get('paragraph_index')
                if para_index is not None:
                    para_indices.append(para_index)
                
                # 也支持 paragraph_indices 列表
                indices_list = issue.location.get('paragraph_indices')
                if indices_list:
                    # 限制每个规则最多标注3个段落，避免文档过大
                    para_indices.extend(indices_list[:3])
                
                # 尝试从 errors 消息中提取段落索引
                errors = issue.location.get('errors', [])
                if errors:
                    for error in errors:
                        if "段落 " in str(error):
                            try:
                                idx = int(str(error).split("段落 ")[1].split(":")[0])
                                if idx not in para_indices:
                                    para_indices.append(idx)
                            except (ValueError, IndexError):
                                pass
            else:
                para_index = getattr(issue, 'paragraph_index', None)
                if para_index is not None:
                    para_indices.append(para_index)
            
            # 将问题添加到对应的段落
            if para_indices:
                for para_idx in para_indices:
                    grouped[para_idx].append(issue)
            else:
                # 如果没有段落索引，添加到特殊键 None，稍后处理
                grouped[None].append(issue)
        
        return dict(grouped)
    
    def _annotate_paragraph(self, para_index: int, issues: List[Any]):
        """对单个段落应用标注（三级降级）"""
        
        # 获取段落
        if para_index >= len(self.doc.paragraphs):
            self.annotation_log.append(f"段落索引 {para_index} 超出范围")
            return
        
        target_para = self.doc.paragraphs[para_index]
        
        # 方法1：优先尝试独立段落标注
        try:
            self._annotate_independent_paragraph(target_para, issues)
            self.annotation_log.append(f"段落 {para_index}: 使用独立段落标注")
            return
        except Exception as e:
            pass
        
        # 方法2：降级为段落末尾追加
        try:
            self._annotate_inline_suffix(target_para, issues)
            self.annotation_log.append(f"段落 {para_index}: 使用末尾追加标注")
            return
        except Exception as e:
            pass
        
        # 方法3：仅记录到日志
        self.annotation_log.append(f"段落 {para_index}: 标注失败，仅记录报告")
        self.failed_count += 1
    
    def _annotate_independent_paragraph(self, para: Paragraph, issues: List[Any]):
        """
        方法1：使用内联标注 + 高亮（不再插入新段落，避免文档过大）
        
        效果：简洁，不增加页数
        """
        # 1. 对违规段落做黄色高亮
        self._highlight_paragraph(para)
        
        # 2. 构建简洁的标注文本
        annotation_text = self._build_annotation_text(issues)
        
        # 3. 在段落末尾添加内联标注（不再插入新段落）
        # 使用换行符分隔
        suffix = "\n" + "─" * 30 + "\n" + annotation_text
        
        run = para.add_run(suffix)
        run.font.color.rgb = self.ANNOTATION_FONT_COLOR
        run.font.bold = self.ANNOTATION_FONT_BOLD
        run.font.size = self.ANNOTATION_FONT_SIZE
    
    def _annotate_inline_suffix(self, para: Paragraph, issues: List[Any]):
        """
        方法2：在段落末尾追加 Run（降级方案）
        
        适用场景：段落在表格单元格内等无法插入独立段落的情况
        """
        # 1. 对段落做黄色高亮
        self._highlight_paragraph(para)
        
        # 2. 构建标注文本
        combined = ' | '.join(
            f'[{getattr(i, "rule_id", "?")}]{getattr(i, "message", "")[:30]}'
            for i in issues
        )
        suffix = f' 【系统审查建议：{combined}】'
        
        # 3. 追加 Run
        run = para.add_run(suffix)
        run.font.color.rgb = self.ANNOTATION_FONT_COLOR
        run.font.bold = self.ANNOTATION_FONT_BOLD
        run.font.size = self.ANNOTATION_FONT_SIZE
    
    def _highlight_paragraph(self, para: Paragraph, highlight_scope: str = 'paragraph'):
        """
        高亮段落或 run
        
        Args:
            para: 段落对象
            highlight_scope: 'paragraph' 或 'run'
        """
        if highlight_scope == 'paragraph':
            # 段落级高亮
            for run in para.runs:
                run.font.highlight_color = self.HIGHLIGHT_COLOR
        else:
            # run 级高亮（由调用方指定具体 run）
            pass
    
    def _highlight_runs(self, para: Paragraph, run_indices: List[int]):
        """高亮指定的 run"""
        for i, run in enumerate(para.runs):
            if i in run_indices:
                run.font.highlight_color = self.HIGHLIGHT_COLOR
    
    def _insert_paragraph_after(self, para: Paragraph) -> Paragraph:
        """
        在指定段落后插入新段落
        
        使用 python-docx 安全 API
        """
        # 创建新的 w:p 元素
        new_p = OxmlElement('w:p')
        
        # 在当前段落之后插入
        para._element.addnext(new_p)
        
        # 创建 Paragraph 对象
        new_para = Paragraph(new_p, para._parent)
        
        return new_para
    
    def _build_annotation_text(self, issues: List[Any]) -> str:
        """构建简洁的标注文本"""
        lines = ["【系统审查建议】"]
        
        for idx, issue in enumerate(issues, 1):
            rule_id = getattr(issue, 'rule_id', '?')
            message = getattr(issue, 'message', '')
            
            # 简化消息，只取第一行
            main_msg = message.split('\n')[0] if message else ""
            # 截断过长的消息
            if len(main_msg) > 40:
                main_msg = main_msg[:40] + "..."
            
            lines.append(f"{idx}. [{rule_id}] {main_msg}")
        
        return "\n".join(lines)
    
    def save(self, output_path: Optional[str] = None) -> str:
        """
        保存文档
        
        Args:
            output_path: 输出路径，默认在原文件名前加后缀
            
        Returns:
            保存的文件路径
        """
        if output_path is None:
            output_path = self.output_path
        
        if output_path is None:
            raise ValueError("未指定输出路径")
        
        self.doc.save(output_path)
        
        return output_path
    
    def get_log(self) -> List[str]:
        """获取标注日志"""
        return self.annotation_log


def annotate_document(input_path: str, issues: List[Any], 
                     output_path: Optional[str] = None) -> Tuple[str, int, int, List[str]]:
    """
    标注文档的便捷函数
    
    Args:
        input_path: 输入文档路径
        issues: Issue 列表
        output_path: 输出路径，默认自动生成
        
    Returns:
        (output_path, annotated_count, failed_count, log)
    """
    from docx import Document
    
    # 如果没有指定输出路径，自动生成
    if output_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        basename = os.path.splitext(os.path.basename(input_path))[0]
        output_path = f"{basename}_审查结果_{timestamp}.docx"
    
    # 复制原文件
    shutil.copy2(input_path, output_path)
    
    # 打开副本
    doc = Document(output_path)
    
    # 执行标注
    annotator = SafeAnnotator(doc, issues, output_path)
    annotated, failed = annotator.annotate_all()
    
    # 保存
    doc.save(output_path)
    
    return output_path, annotated, failed, annotator.get_log()


def generate_report(input_path: str, issues: List[Any],
                   output_path: Optional[str] = None) -> str:
    """
    生成文本审查报告
    
    Args:
        input_path: 输入文档路径
        issues: Issue 列表
        output_path: 输出路径，默认自动生成
        
    Returns:
        报告文件路径
    """
    # 如果没有指定输出路径，自动生成
    if output_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        basename = os.path.splitext(os.path.basename(input_path))[0]
        output_path = f"{basename}_审查报告_{timestamp}.txt"
    
    # 生成报告内容
    lines = []
    lines.append("=" * 60)
    lines.append("北大光华 EMBA 论文格式审查报告")
    lines.append("=" * 60)
    lines.append(f"审查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"论文文件: {os.path.basename(input_path)}")
    lines.append("")
    
    # 统计
    error_count = sum(1 for i in issues if getattr(i, 'severity', '') == 'error')
    warning_count = sum(1 for i in issues if getattr(i, 'severity', '') == 'warning')
    info_count = sum(1 for i in issues if getattr(i, 'severity', '') == 'info')
    
    lines.append("-" * 60)
    lines.append("审查结果摘要")
    lines.append("-" * 60)
    lines.append(f"发现问题总数: {len(issues)}")
    lines.append(f"  错误: {error_count}")
    lines.append(f"  警告: {warning_count}")
    lines.append(f"  信息: {info_count}")
    lines.append("")
    
    # 详细问题清单
    lines.append("-" * 60)
    lines.append("详细问题清单")
    lines.append("-" * 60)
    
    for idx, issue in enumerate(issues, 1):
        rule_id = getattr(issue, 'rule_id', '?')
        severity = getattr(issue, 'severity', 'info')
        message = getattr(issue, 'message', '')
        location = getattr(issue, 'location', None)
        para_idx = location.get('paragraph_index', 'N/A') if location else 'N/A'
        
        lines.append(f"[#{idx}] 规则 {rule_id} | 严重程度: {severity} | 段落: {para_idx}")
        lines.append(f"     {message}")
        lines.append("")
    
    # 写入文件
    content = "\n".join(lines)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_path
