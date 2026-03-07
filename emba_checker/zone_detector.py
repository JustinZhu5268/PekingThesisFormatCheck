# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 区域识别模块
根据特征文本和样式标记每个段落的 zone
"""

import re
import sys
import os
from typing import Dict, List, Optional, Tuple

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from docx.document import Document
from docx.oxml.ns import qn

try:
    from emba_checker import config
except ImportError:
    import config


class ZoneDetector:
    """文档区域识别器"""
    
    def __init__(self, doc: Document):
        self.doc = doc
        self.zone_map: Dict[int, str] = {}
        self._detect()
    
    def _detect(self):
        """执行区域检测"""
        self.zone_map = {}
        current_zone = "cover"
        
        for i, para in enumerate(self.doc.paragraphs):
            text = para.text.strip()
            
            # 跳过空段落
            if not text:
                self.zone_map[i] = current_zone
                continue
            
            # 检查是否为分界标志（按优先级从后往前）
            # 先检查更具体的标题（如参考文献、致谢），再检查通用标题（如章标题）
            
            # 致谢
            if re.match(r"^致\s*谢$", text):
                current_zone = "acknowledgment"
            
            # 附录
            elif re.match(r"^附录", text):
                current_zone = "appendix"
            
            # 参考文献
            elif re.match(r"^参考文献$", text):
                current_zone = "references"
            
            # 正文章节标题
            elif re.match(r"^第[一二三四五六七八九十]+章", text):
                current_zone = "body_chapter"
            
            # 目录
            elif re.match(r"^目\s*录$", text):
                current_zone = "toc"
            
            # 英文摘要
            elif re.match(r"^ABSTRACT$", text, re.IGNORECASE):
                current_zone = "abstract_en"
            
            # 中文摘要
            elif re.match(r"^摘\s*要$", text):
                current_zone = "abstract_cn"
            
            # 原创性声明
            elif "原创性声明" in text:
                current_zone = "declaration"
            
            # 版权声明
            elif "版权声明" in text:
                current_zone = "copyright"
            
            self.zone_map[i] = current_zone
    
    def get_zone(self, paragraph_index: int) -> str:
        """获取指定段落的区域"""
        return self.zone_map.get(paragraph_index, "unknown")
    
    def get_zone_ranges(self) -> Dict[str, List[Tuple[int, int]]]:
        """获取每个区域的段落索引范围"""
        ranges = {}
        
        current_zone = None
        start_idx = 0
        
        for i, zone in self.zone_map.items():
            if zone != current_zone:
                # 保存前一个区域的范围
                if current_zone is not None:
                    if current_zone not in ranges:
                        ranges[current_zone] = []
                    ranges[current_zone].append((start_idx, i - 1))
                
                # 开始新区域
                current_zone = zone
                start_idx = i
        
        # 保存最后一个区域
        if current_zone is not None:
            if current_zone not in ranges:
                ranges[current_zone] = []
            ranges[current_zone].append((start_idx, len(self.zone_map) - 1))
        
        return ranges
    
    def get_paragraphs_in_zone(self, zone: str) -> List[int]:
        """获取指定区域的所有段落索引"""
        return [i for i, z in self.zone_map.items() if z == zone]
    
    def get_zone_stats(self) -> Dict[str, int]:
        """获取各区域的段落统计"""
        stats = {}
        for zone in config.ZONES:
            count = sum(1 for z in self.zone_map.values() if z == zone)
            if count > 0:
                stats[zone] = count
        return stats
    
    def __repr__(self):
        stats = self.get_zone_stats()
        return f"ZoneDetector(zones={len(stats)}, map={self.zone_map})"


def detect_zones(doc: Document) -> Dict[int, str]:
    """
    遍历 doc.paragraphs，根据特征文本和样式标记每个段落的 zone
    返回 {paragraph_index: zone_name}
    
    Args:
        doc: python-docx Document 对象
        
    Returns:
        段落索引到区域的映射字典
    """
    detector = ZoneDetector(doc)
    return detector.zone_map


def get_zone_for_paragraph(doc: Document, paragraph_index: int) -> str:
    """
    获取指定段落的区域
    
    Args:
        doc: python-docx Document 对象
        paragraph_index: 段落索引
        
    Returns:
        区域名称
    """
    zone_map = detect_zones(doc)
    return zone_map.get(paragraph_index, "unknown")


def get_zone_ranges(doc: Document) -> Dict[str, List[Tuple[int, int]]]:
    """
    获取每个区域的段落索引范围
    
    Args:
        doc: python-docx Document 对象
        
    Returns:
        {zone_name: [(start_idx, end_idx), ...]}
    """
    detector = ZoneDetector(doc)
    return detector.get_zone_ranges()


# ============================================================================
# 区域检测的辅助函数
# ============================================================================

def is_cover_page(para) -> bool:
    """判断是否为封面页段落"""
    text = para.text.strip()
    # 封面常见关键词
    cover_keywords = ["论文题目", "专业学位", "导师", "学号", "研究方向"]
    return any(kw in text for kw in cover_keywords)


def is_copyright_page(para) -> bool:
    """判断是否为版权声明页段落"""
    text = para.text.strip()
    return "版权声明" in text or "收存和保管" in text


def is_declaration_page(para) -> bool:
    """判断是否为原创性声明页段落"""
    text = para.text.strip()
    return "原创性声明" in text or "授权说明" in text


def is_abstract_cn(para) -> bool:
    """判断是否为中文摘要段落"""
    # 检查样式
    if para.style and "标题" in para.style.name:
        text = para.text.strip()
        if re.match(r"^摘\s*要$", text):
            return True
    return False


def is_abstract_en(para) -> bool:
    """判断是否为英文摘要段落"""
    if para.style and "标题" in para.style.name:
        text = para.text.strip()
        if re.match(r"^ABSTRACT$", text, re.IGNORECASE):
            return True
    return False


def is_toc(para) -> bool:
    """判断是否为目录段落"""
    if para.style and "标题" in para.style.name:
        text = para.text.strip()
        if re.match(r"^目\s*录$", text):
            return True
    return False


def is_body_chapter(para) -> bool:
    """判断是否为正文章节段落"""
    text = para.text.strip()
    # 章标题
    if re.match(r"^第[一二三四五六七八九十]+章", text):
        return True
    return False


def is_references(para) -> bool:
    """判断是否为参考文献段落"""
    if para.style and "标题" in para.style.name:
        text = para.text.strip()
        if re.match(r"^参考文献$", text):
            return True
    return False


def is_appendix(para) -> bool:
    """判断是否为附录段落"""
    if para.style and "标题" in para.style.name:
        text = para.text.strip()
        if re.match(r"^附录", text):
            return True
    return False


def is_acknowledgment(para) -> bool:
    """判断是否为致谢段落"""
    if para.style and "标题" in para.style.name:
        text = para.text.strip()
        if re.match(r"^致\s*谢$", text):
            return True
    return False


# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    # 简单测试
    from docx import Document
    
    # 创建一个测试文档
    doc = Document()
    
    # 添加封面内容
    doc.add_paragraph("封面内容...")
    doc.add_paragraph("论文题目：XXXXXXXX")
    
    # 添加版权声明
    doc.add_paragraph("版权声明")
    doc.add_paragraph("本论文作者完全同意...")
    
    # 添加中文摘要（使用 Heading 1 样式）
    para = doc.add_paragraph()
    para.add_run("摘要")
    
    doc.add_paragraph("这是中文摘要内容...")
    
    # 添加英文摘要
    para = doc.add_paragraph()
    para.add_run("ABSTRACT")
    
    doc.add_paragraph("This is English abstract...")
    
    # 添加目录
    para = doc.add_paragraph()
    para.add_run("目录")
    
    doc.add_paragraph("第一章 引言 ............1")
    
    # 添加正文
    para = doc.add_paragraph()
    para.add_run("第一章 引言")
    
    doc.add_paragraph("这是正文第一章的内容...")
    
    # 添加参考文献
    para = doc.add_paragraph()
    para.add_run("参考文献")
    
    doc.add_paragraph("[1] 张三. 论文标题. 出版社, 2020.")
    
    # 添加致谢
    para = doc.add_paragraph()
    para.add_run("致谢")
    
    doc.add_paragraph("感谢导师...")
    
    # 测试区域检测
    zone_map = detect_zones(doc)
    
    print("段落区域检测结果:")
    print("-" * 40)
    for i, para in enumerate(doc.paragraphs):
        text = para.text[:30] + "..." if len(para.text) > 30 else para.text
        zone = zone_map.get(i, "unknown")
        print(f"段落 {i}: [{zone:15}] {text}")
    
    print("\n区域统计:")
    print("-" * 40)
    detector = ZoneDetector(doc)
    stats = detector.get_zone_stats()
    for zone, count in sorted(stats.items()):
        print(f"  {zone:20}: {count} 段落")
