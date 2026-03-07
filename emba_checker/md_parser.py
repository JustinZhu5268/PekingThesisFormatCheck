# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - MD 清单解析器
自动从 MD 清单中提取可编程规则
"""

import re
import json
import sys
import os
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path

# 添加父目录到路径，以便模块导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from emba_checker import config
except ImportError:
    # 如果作为脚本运行，从当前目录导入
    import config


class MDParser:
    """MD 清单解析器"""
    
    def __init__(self, md_path: str):
        self.md_path = md_path
        self.content = ""
        self.rules = []
        self.current_section = None
        self.section_counter = {}  # {prefix: int}
        
    def load(self):
        """加载 MD 文件"""
        with open(self.md_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
    
    def parse(self) -> List[Dict]:
        """
        解析 MD 清单，生成结构化规则列表
        返回: list[dict]，每条规则包含 MD 原始信息 + 推断的 check_type/conditions
        """
        self.load()
        self.rules = []
        self.current_section = None
        self.section_counter = {}
        
        lines = self.content.split('\n')
        
        for line in lines:
            stripped = line.strip()
            
            # 1. 识别章节标题
            if self._is_section_heading(stripped):
                self.current_section = self._extract_section_name(stripped)
                continue
            
            # 2. 跳过非表格行、表头行、分隔线
            if not self._is_table_row(stripped):
                continue
            
            # 3. 解析表格列
            rule = self._parse_table_row(stripped)
            if rule:
                self.rules.append(rule)
        
        return self.rules
    
    def _is_section_heading(self, line: str) -> bool:
        """判断是否为章节标题"""
        # 一级章节 ## 二、封面页格式
        # 二级章节 ### 11.1 图的要求
        return line.startswith('## ') and not self._is_meta_line(line)
    
    def _is_meta_line(self, line: str) -> bool:
        """判断是否为元信息行（不包含在规则中）"""
        return '附：' in line or '可编程' in line or line.startswith('>')
    
    def _extract_section_name(self, line: str) -> str:
        """提取章节名称"""
        # 去除 ## 或 ### 前缀
        name = line.lstrip('#').strip()
        return name
    
    def _is_table_row(self, line: str) -> bool:
        """判断是否为表格数据行"""
        if not line.startswith('|'):
            return False
        # 跳过表头和分隔线
        if '---' in line or '要素' in line[:20]:
            return False
        return True
    
    def _parse_table_row(self, line: str) -> Optional[Dict]:
        """解析表格行"""
        cells = [c.strip() for c in line.split('|') if c.strip()]
        if len(cells) < 4:
            return None
        
        # 提取各列
        element_name = cells[0].replace('**', '')  # 去加粗
        format_requirement = cells[1]
        urgency = cells[2].strip()
        programmability = cells[3].strip()
        detection_method = cells[4] if len(cells) > 4 else ""
        
        # 过滤：仅保留 ✅ 和 ⚠️
        is_auto = '\u2705' in programmability  # ✅
        is_semi = '\u26a0' in programmability   # ⚠️
        if not is_auto and not is_semi:
            return None
        
        automation_level = "auto" if is_auto else "semi"
        
        # 生成 rule_id
        prefix = self._section_to_prefix(self.current_section)
        self.section_counter[prefix] = self.section_counter.get(prefix, 0) + 1
        rule_id = f"{prefix}_{self.section_counter[prefix]:02d}"
        
        # 推断属性
        group = self._infer_group(self.current_section, element_name, self._infer_zones(self.current_section))
        zones = self._infer_zones(self.current_section)
        check_type, conditions = self._infer_check_type(
            format_requirement, detection_method, element_name
        )
        engine = self._infer_engine(automation_level, check_type, element_name)
        
        return {
            "rule_id": rule_id,
            "md_source": self.current_section,
            "md_source_key": f"{self.current_section}::{element_name}",
            "element_name": element_name,
            "format_requirement": format_requirement,
            "automation_level": automation_level,
            "urgency": urgency,
            "target_group": group,
            "target_zone": zones,
            "engine": engine,
            "check_type": check_type,
            "conditions": conditions,
            "detection_method": detection_method,
            "error_message": f"{element_name}格式不符：{format_requirement[:80]}",
            "enabled": True,
        }
    
    def _section_to_prefix(self, section_title: str) -> str:
        """章节标题转换为前缀"""
        if not section_title:
            return "MISC"
        
        for keyword, prefix in config.PREFIX_MAP.items():
            if keyword in section_title:
                return prefix
        return "MISC"
    
    def _infer_group(self, prefix: str, detection_method: str) -> str:
        """推断所属分组"""
        group_inference = {
            "PAGE": "Group1_Global",
            "HEADER": "Group1_HeaderFooter",
            "FOOT": "Group4_Footnotes",
            "REF_LIST": "Group5_References",
            "REF_TYPE": "Group5_References",
            "FIG": "Group3_Figures",
            "TBL": "Group3_Tables",
            "FIGTBL": "Group3_Tables",
        }
        
        if prefix in group_inference:
            return group_inference[prefix]
        
        # 交叉引用检查
        if "对应" in detection_method or "一一" in detection_method:
            return "Group6_CrossRef"
        
        return "Group2_Paragraphs"
    
    def _infer_zones(self, section_title: str) -> List[str]:
        """推断生效区域"""
        zones = []
        
        section_to_zones = {
            "封面": ["cover"],
            "版权": ["copyright"],
            "原创性": ["declaration"],
            "授权": ["declaration"],
            "承诺": ["declaration"],
            "摘要格式": ["abstract_cn"],
            "英文摘要": ["abstract_en"],
            "目录": ["toc"],
            "正文标题": ["body_chapter"],
            "正文段落": ["body_chapter"],
            "正文引用": ["body_chapter"],
            "图的要求": ["body_chapter"],
            "表的要求": ["body_chapter"],
            "通用图表": ["body_chapter"],
            "表达式": ["body_chapter"],
            "公式": ["body_chapter"],
            "脚注": ["body_chapter"],
            "参考文献": ["references"],
            "附录": ["appendix"],
            "致谢": ["acknowledgment"],
            "论文题目": ["cover"],
            "文字表达": ["body_chapter"],
            "研究问题": ["body_chapter"],
            "论文结构": ["body_chapter"],
            "案例写作": ["body_chapter"],
            "文献综述": ["body_chapter"],
            "案例分析": ["body_chapter"],
            "研究结论": ["body_chapter"],
        }
        
        for keyword, zone_list in section_to_zones.items():
            if keyword in section_title:
                return zone_list
        
        # 页面设置和页眉页码是全局的
        if "页面" in section_title or "页眉" in section_title or "页码" in section_title:
            return ["cover", "abstract_cn", "abstract_en", "toc", "body_chapter", "references", "appendix", "acknowledgment"]
        
        if "标点" in section_title:
            return ["abstract_cn", "body_chapter"]
        
        return ["body_chapter"]
    
    def _infer_check_type(self, format_req: str, detection_method: str, 
                          element_name: str) -> Tuple[str, Dict]:
        """
        推断 check_type 和 conditions
        优先级：text_match > regex > count > forbidden > cross_ref > global > style > unknown
        """
        dm = detection_method
        fr = format_req
        
        # 1. 文本精确匹配（固定格式）
        if any(kw in fr for kw in ["固定格式", "请勿做任何修改", "精确匹配"]):
            return "text_match", {"match_mode": "exact"}
        if "文本匹配" in dm or "精确匹配" in dm:
            return "text_match", {"match_mode": "contains"}
        
        # 2. 正则匹配
        if "正则" in dm or "Unicode" in dm or "编号" in element_name:
            return "regex_match", {"match_mode": "must_match"}
        
        # 3. 计数/统计
        if re.search(r"(不超过|不少于|至少|最多|最少)\s*\d+", fr) or "字数" in dm:
            return "count_check", self._parse_count_conditions(fr)
        
        # 4. 禁用词
        if any(kw in fr for kw in ["禁止引用", "禁止使用", "不得", "禁用"]):
            return "forbidden_words", {"match_mode": "any"}
        
        # 5. 交叉引用
        if "对应" in dm or "引用匹配" in dm or "一一" in fr:
            return "cross_reference", {"must_match": True}
        
        # 6. 全局属性
        if any(kw in fr for kw in ["A4", "页边距", "cm", "纸张", "距边界"]):
            return "global_property", self._parse_global_conditions(fr)
        
        # 7. 段落样式
        style_kw = ["字体", "字号", "号", "宋体", "黑体", "仿宋", "Times",
                    "居中", "对齐", "缩进", "行距", "段前", "段后", "加粗", "倍行距"]
        if any(kw in fr for kw in style_kw):
            return "paragraph_style", self._parse_style_conditions(fr)
        
        # 8. 无法推断
        return "unknown", {"_needs_manual_review": True, "_raw_requirement": fr}
    
    def _parse_style_conditions(self, format_req: str) -> Dict:
        """从格式要求文本中提取段落样式条件"""
        cond = {}
        fr = format_req
        
        # 字体
        font_cn_map = {"黑体": "黑体", "宋体": "宋体", "仿宋": "仿宋", "楷体": "楷体"}
        for cn, val in font_cn_map.items():
            if cn in fr:
                cond["font_name_cn"] = val
                break
        
        if "Times New Roman" in fr or "Times" in fr:
            cond["font_name_en"] = "Times New Roman"
        if "Arial" in fr:
            cond["font_name_en"] = "Arial"
        
        # 字号
        for cn_size, pt in config.FONT_SIZE_MAP.items():
            if cn_size in fr:
                cond["font_size_pt"] = pt
                break
        
        # 对齐
        if "居中" in fr:
            cond["alignment"] = "CENTER"
        elif "两端对齐" in fr:
            cond["alignment"] = "JUSTIFY"
        elif "左对齐" in fr:
            cond["alignment"] = "LEFT"
        
        # 加粗
        if "加粗" in fr:
            cond["bold"] = True
        
        # 行距
        m = re.search(r"(\d+\.?\d*)\s*倍行距", fr)
        if m:
            cond["line_spacing_type"] = "MULTIPLE"
            cond["line_spacing_value"] = float(m.group(1))
        
        m2 = re.search(r"行距[:：]?\s*(\d+)\s*磅", fr)
        if m2:
            cond["line_spacing_type"] = "EXACTLY"
            cond["line_spacing_value_pt"] = int(m2.group(1))
        
        # 首行缩进
        m3 = re.search(r"首行[空缩]+(\d+\.?\d*)\s*字符", fr)
        if m3:
            cond["first_line_indent_char"] = float(m3.group(1))
        
        # 悬挂缩进
        m4 = re.search(r"悬挂缩进\s*(\d+\.?\d*)\s*字符", fr)
        if m4:
            cond["hanging_indent_char"] = float(m4.group(1))
        
        # 段前段后
        m5 = re.search(r"段前\s*(\d+)\s*磅", fr)
        if m5:
            cond["space_before_pt"] = int(m5.group(1))
        
        m6 = re.search(r"段后\s*(\d+)\s*磅", fr)
        if m6:
            cond["space_after_pt"] = int(m6.group(1))
        
        return cond
    
    def _parse_global_conditions(self, format_req: str) -> Dict:
        """从格式要求中提取全局属性条件"""
        cond = {}
        fr = format_req
        
        # 纸张尺寸
        mm = re.findall(r"(\d+)\s*[x×]\s*(\d+)\s*mm", fr)
        if mm:
            cond["page_width_cm"] = int(mm[0][0]) / 10
            cond["page_height_cm"] = int(mm[0][1]) / 10
        
        # 页边距
        for label, key in [("上", "top_margin_cm"), ("下", "bottom_margin_cm"),
                          ("左", "left_margin_cm"), ("右", "right_margin_cm")]:
            m = re.search(label + r"\s*(\d+\.?\d*)\s*cm", fr)
            if m:
                cond[key] = float(m.group(1))
        
        # 页眉/页脚距边界
        m = re.search(r"页眉距边界\s*(\d+\.?\d*)\s*cm", fr)
        if m:
            cond["header_distance_cm"] = float(m.group(1))
        
        m = re.search(r"页脚距边界\s*(\d+\.?\d*)\s*cm", fr)
        if m:
            cond["footer_distance_cm"] = float(m.group(1))
        
        return cond
    
    def _parse_count_conditions(self, format_req: str) -> Dict:
        """从格式要求中提取计数条件"""
        cond = {}
        fr = format_req
        
        m = re.search(r"不超过\s*(\d+)", fr)
        if m:
            cond["max_value"] = int(m.group(1))
        
        m2 = re.search(r"(不少于|至少)\s*(\d+)", fr)
        if m2:
            cond["min_value"] = int(m2.group(2))
        
        if "字" in format_req:
            cond["count_type"] = "chinese_chars"
        elif "个" in format_req:
            cond["count_type"] = "items"
        elif "篇" in format_req:
            cond["count_type"] = "references"
        
        return cond
    
    def _infer_engine(self, automation_level: str, check_type: str, 
                     element_name: str) -> str:
        """推断引擎类型"""
        if check_type == "ai_semantic":
            return "Claude"
        
        claude_keywords = ["标点滥用", "翻译一致性", "段落长度", "句子长度",
                          "图表清晰度", "禁止病句错字", "统一性", "专有名词",
                          "数据来源", "讨论深度", "研究不足", "文献综述"]
        
        if any(kw in element_name for kw in claude_keywords):
            return "Python+Claude"
        
        if automation_level == "semi":
            return "Python+Manual"
        
        return "Python"
    
    def _infer_group(self, section: str, element_name: str, 
                     target_zones: List[str]) -> str:
        """
        推断规则所属的检查组
        
        Args:
            section: MD 章节名称
            element_name: 要素名称
            target_zones: 目标区域列表
            
        Returns:
            target_group 字符串
        """
        # 根据 section 推断
        section_group_map = {
            "三、页面设置": "Group1_Global",
            "四、页眉页码设置": "Group1_HeaderFooter",
            "七、图表规范": "Group3_Figures",
            "八、脚注规范": "Group4_Footnotes",
            "九、参考文献格式": "Group5_References",
            "十、文本规范性检查": "Group2_Paragraphs",
        }
        
        for sec_key, group in section_group_map.items():
            if sec_key in section:
                return group
        
        # 根据 element_name 关键词推断
        if any(kw in element_name for kw in ["页眉", "页码"]):
            return "Group1_HeaderFooter"
        
        if any(kw in element_name for kw in ["图", "表"]):
            if "图" in element_name:
                return "Group3_Figures"
            return "Group3_Tables"
        
        if any(kw in element_name for kw in ["脚注", " footnote"]):
            return "Group4_Footnotes"
        
        if any(kw in element_name for kw in ["参考文献", "引用", "文献"]):
            return "Group5_References"
        
        # 根据 target_zone 推断
        if "references" in target_zones:
            return "Group5_References"
        
        if any(z.startswith("fig") for z in target_zones):
            return "Group3_Figures"
        
        if any(z.startswith("table") for z in target_zones):
            return "Group3_Tables"
        
        # 默认到段落检查组
        return "Group2_Paragraphs"


def parse_md_to_rules(md_path: str) -> List[Dict]:
    """
    解析 MD 清单文件的便捷函数
    """
    parser = MDParser(md_path)
    return parser.parse()


if __name__ == "__main__":
    # 测试
    md_path = r"D:\Projects\ThesisFormatCheck\docs\EMBA论文格式排版要求清单完善版.md"
    rules = parse_md_to_rules(md_path)
    
    print(f"解析出 {len(rules)} 条规则")
    
    # 统计
    known = [r for r in rules if r["check_type"] != "unknown"]
    unknown = [r for r in rules if r["check_type"] == "unknown"]
    
    print(f"  Python 推断成功: {len(known)} 条")
    print(f"  需人工: {len(unknown)} 条")
    
    # 输出前3条
    for r in rules[:3]:
        print(f"\n{r['rule_id']}: {r['element_name']}")
        print(f"  check_type: {r['check_type']}")
        print(f"  conditions: {r['conditions']}")
