# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - 工具函数模块
包含单位换算、XML 安全读取、中文字体读取等工具函数
"""

import os
import sys

# 添加当前目录到路径（用于直接运行）
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from lxml import etree
from docx.shared import Pt, Emu, Twips
from docx.oxml.ns import qn
import re
from typing import Optional, Union, List, Dict, Any

try:
    import config
except ImportError:
    # 如果作为包运行
    pass


# ============================================================================
# 单位换算函数
# ============================================================================

def emu_to_cm(emu: int) -> float:
    """EMU 转厘米"""
    return emu / config.EMU_PER_CM


def cm_to_emu(cm: float) -> int:
    """厘米转 EMU"""
    return int(cm * config.EMU_PER_CM)


def emu_to_pt(emu: int) -> float:
    """EMU 转磅值"""
    return emu / config.EMU_PER_PT


def pt_to_emu(pt: float) -> int:
    """磅值转 EMU"""
    return int(pt * config.EMU_PER_PT)


def emu_to_twips(emu: int) -> int:
    """EMU 转 Twips (1/20 磅)"""
    return emu // (config.EMU_PER_PT // 20)


def twips_to_emu(twips: int) -> int:
    """Twips 转 EMU"""
    return twips * (config.EMU_PER_PT // 20)


def pt_to_twips(pt: float) -> int:
    """磅值转 Twips"""
    return int(pt * 20)


def twips_to_pt(twips: int) -> float:
    """Twips 转磅值"""
    return twips / 20.0


def char_to_cm(chars: float) -> float:
    """
    字符数转厘米
    默认中文字符宽度约为 0.74cm (2字符 = 1.48cm)
    """
    return chars * 0.37


def cm_to_char(cm: float) -> float:
    """厘米转字符数"""
    return cm / 0.37


# ============================================================================
# XML 安全读取函数
# ============================================================================

def safe_read_xml(element, xpath_expr: str, default: Any = None) -> Any:
    """
    安全读取 XML 元素属性
    
    Args:
        element: lxml XML 元素
        xpath_expr: XPath 表达式
        default: 默认返回值
        
    Returns:
        匹配的文本内容或默认值
    """
    try:
        if element is None:
            return default
        result = element.xpath(xpath_expr)
        if result:
            # 返回第一个匹配结果
            if isinstance(result[0], str):
                return result[0]
            # 如果是元素，返回其文本内容
            return result[0].text if result[0].text else default
        return default
    except Exception:
        return default


def get_element_attr(element, attr_name: str, default: Any = None) -> Any:
    """安全读取 XML 元素属性"""
    try:
        if element is None:
            return default
        return element.get(attr_name, default)
    except Exception:
        return default


# ============================================================================
# 字体相关函数
# ============================================================================

def get_east_asia_font(run) -> Optional[str]:
    """
    读取中文字体（eastAsia 属性）
    
    python-docx 的 run.font.name 通常返回西文字体名，
    中文字体存储在 eastAsia 属性中，需要通过 XML 读取
    """
    try:
        # 尝试通过 python-docx API 读取
        # run._element 是 CT_R (Run) 元素
        rpr = run._element.find(qn('w:rPr'))
        if rpr is not None:
            rFonts = rpr.find(qn('w:rFonts'))
            if rFonts is not None:
                # 读取 w:eastAsia 属性
                east_asia = rFonts.get(qn('w:eastAsia'))
                if east_asia:
                    return east_asia
        return None
    except Exception:
        return None


def get_font_name(run) -> Dict[str, Optional[str]]:
    """
    获取字体的完整信息
    
    Returns:
        Dict with keys: 'name' (western), 'east_asia' (chinese), 'name_cs' (complex script)
    """
    result = {
        'name': None,
        'east_asia': None,
        'name_cs': None,
    }
    
    try:
        # 尝试读取西文字体名
        if run.font and run.font.name:
            result['name'] = run.font.name
            
        # 尝试读取中文字体
        result['east_asia'] = get_east_asia_font(run)
        
        # 尝试读取复杂脚本字体
        try:
            rpr = run._element.find(qn('w:rPr'))
            if rpr is not None:
                rFonts = rpr.find(qn('w:rFonts'))
                if rFonts is not None:
                    result['name_cs'] = rFonts.get(qn('w:nameCs'))
        except Exception:
            pass
            
    except Exception:
        pass
    
    return result


def get_font_size(run) -> Optional[float]:
    """
    获取字体大小（磅值）
    
    Returns:
        字号（磅值），如 12.0 或 None
    """
    try:
        if run.font and run.font.size:
            return emu_to_pt(run.font.size)
        return None
    except Exception:
        return None


def get_font_bold(run) -> Optional[bool]:
    """获取加粗属性"""
    try:
        if run.font and run.font.bold is not None:
            return run.font.bold
        return None
    except Exception:
        return None


def get_font_italic(run) -> Optional[bool]:
    """获取斜体属性"""
    try:
        if run.font and run.font.italic is not None:
            return run.font.italic
        return None
    except Exception:
        return None


def is_chinese_char(char: str) -> bool:
    """判断是否为中文字符"""
    if not char:
        return False
    return '\u4e00' <= char <= '\u9fff'


def is_english_char(char: str) -> bool:
    """判断是否为英文字符"""
    if not char:
        return False
    return char.isascii() and char.isalpha()


def is_number_char(char: str) -> bool:
    """判断是否为数字字符"""
    if not char:
        return False
    return char.isdigit()


def is_chinese_punctuation(char: str) -> bool:
    """判断是否为中文标点"""
    return char in config.CHINESE_PUNCTUATION


def is_english_punctuation(char: str) -> bool:
    """判断是否为英文标点"""
    return char in config.ENGLISH_PUNCTUATION


# ============================================================================
# 段落格式相关函数
# ============================================================================

def get_paragraph_alignment(para) -> Optional[str]:
    """
    获取段落对齐方式
    
    Returns:
        'LEFT', 'CENTER', 'RIGHT', 'JUSTIFY', 'DISTRIBUTE' 或 None
    """
    try:
        if para.paragraph_format and para.paragraph_format.alignment:
            alignment = para.paragraph_format.alignment
            # WD_ALIGN_PARAGRAPH 枚举值
            alignment_map = {
                0: 'LEFT',
                1: 'CENTER',
                2: 'RIGHT',
                3: 'JUSTIFY',
                4: 'DISTRIBUTE',
                5: 'LEFT',  # Thai distribution
            }
            return alignment_map.get(alignment, None)
        return None
    except Exception:
        return None


def get_first_line_indent(para) -> Optional[float]:
    """
    获取首行缩进（字符数）
    
    Returns:
        首行缩进字符数，或 None
    """
    try:
        if para.paragraph_format and para.paragraph_format.first_line_indent:
            indent_emu = para.paragraph_format.first_line_indent
            # EMU 转字符数（近似）
            indent_cm = emu_to_cm(abs(indent_emu))
            return cm_to_char(indent_cm)
        return None
    except Exception:
        return None


def get_hanging_indent(para) -> Optional[float]:
    """
    获取悬挂缩进（字符数）
    
    Returns:
        悬挂缩进字符数，或 None
    """
    try:
        if para.paragraph_format and para.paragraph_format.left_indent:
            indent_emu = para.paragraph_format.left_indent
            # 检查是否为悬挂缩进（负值表示悬挂）
            if indent_emu < 0:
                indent_cm = emu_to_cm(abs(indent_emu))
                return cm_to_char(indent_cm)
        return None
    except Exception:
        return None


def get_line_spacing(para) -> Optional[Dict[str, Any]]:
    """
    获取行距信息
    
    Returns:
        Dict with keys: 'type' (MULTIPLE/EXACTLY/AT_LEAST), 'value' (数值), 'unit' (pt/multiple)
    """
    try:
        pf = para.paragraph_format
        if pf and pf.line_spacing:
            result = {}
            
            # 行距类型
            if pf.line_spacing_rule:
                rule_map = {
                    0: 'MULTIPLE',    # EXACTLY
                    1: 'MULTIPLE',    # AT_LEAST
                    2: 'EXACTLY',     # EXACTLY
                    3: 'MULTIPLE',    # MULTIPLE
                    4: 'MULTIPLE',    # DISTRIBUTE
                }
                result['type'] = rule_map.get(pf.line_spacing_rule, 'MULTIPLE')
            
            # 行距值
            if pf.line_spacing:
                spacing_emu = pf.line_spacing
                if result.get('type') == 'MULTIPLE':
                    # 多倍行距需要转换为实际磅值
                    # python-docx 返回的是EMU，我们需要换算
                    result['value'] = emu_to_pt(spacing_emu) / 12.0  # 基准12pt
                    result['unit'] = 'multiple'
                else:
                    result['value'] = emu_to_pt(spacing_emu)
                    result['unit'] = 'pt'
            
            return result
        return None
    except Exception:
        return None


def get_space_before(para) -> Optional[float]:
    """获取段前间距（磅值）"""
    try:
        if para.paragraph_format and para.paragraph_format.space_before:
            return emu_to_pt(para.paragraph_format.space_before)
        return None
    except Exception:
        return None


def get_space_after(para) -> Optional[float]:
    """获取段后间距（磅值）"""
    try:
        if para.paragraph_format and para.paragraph_format.space_after:
            return emu_to_pt(para.paragraph_format.space_after)
        return None
    except Exception:
        return None


# ============================================================================
# 页面属性相关函数
# ============================================================================

def get_page_size(section) -> Dict[str, float]:
    """
    获取页面尺寸
    
    Returns:
        Dict with keys: 'width_cm', 'height_cm'
    """
    try:
        return {
            'width_cm': emu_to_cm(section.page_width),
            'height_cm': emu_to_cm(section.page_height),
        }
    except Exception:
        return {'width_cm': 0, 'height_cm': 0}


def get_page_margins(section) -> Dict[str, float]:
    """
    获取页边距
    
    Returns:
        Dict with keys: 'top_cm', 'bottom_cm', 'left_cm', 'right_cm', 'gutter_cm'
    """
    try:
        return {
            'top_cm': emu_to_cm(section.top_margin),
            'bottom_cm': emu_to_cm(section.bottom_margin),
            'left_cm': emu_to_cm(section.left_margin),
            'right_cm': emu_to_cm(section.right_margin),
            'gutter_cm': emu_to_cm(section.gutter),
        }
    except Exception:
        return {
            'top_cm': 0, 'bottom_cm': 0,
            'left_cm': 0, 'right_cm': 0, 'gutter_cm': 0
        }


# ============================================================================
# 文本处理函数
# ============================================================================

def count_chinese_chars(text: str) -> int:
    """统计中文字符数量"""
    return sum(1 for c in text if is_chinese_char(c))


def count_english_chars(text: str) -> int:
    """统计英文字母数量"""
    return sum(1 for c in text if is_english_char(c))


def count_numbers(text: str) -> int:
    """统计数字数量"""
    return sum(1 for c in text if is_number_char(c))


def count_total_chars(text: str) -> int:
    """统计总字符数（不含空格）"""
    return sum(1 for c in text if not c.isspace())


def count_words(text: str) -> int:
    """统计英文单词数量"""
    return len(re.findall(r'[a-zA-Z]+', text))


def extract_chinese_text(text: str) -> str:
    """提取所有中文字符"""
    return ''.join(c for c in text if is_chinese_char(c))


def extract_english_text(text: str) -> str:
    """提取所有英文字母"""
    return ''.join(c for c in text if is_english_char(c))


# ============================================================================
# 正则匹配函数
# ============================================================================

def match_pattern(text: str, pattern: str, flags: int = 0) -> bool:
    """正则匹配测试"""
    try:
        return bool(re.search(pattern, text, flags))
    except Exception:
        return False


def find_all_matches(text: str, pattern: str, flags: int = 0) -> List[re.Match]:
    """查找所有匹配项"""
    try:
        return list(re.finditer(pattern, text, flags))
    except Exception:
        return []


def replace_pattern(text: str, pattern: str, replacement: str, flags: int = 0) -> str:
    """正则替换"""
    try:
        return re.sub(pattern, replacement, text, flags=flags)
    except Exception:
        return text


# ============================================================================
# 词库加载函数
# ============================================================================

def load_word_list(file_path: str) -> List[str]:
    """
    加载词库文件（每行一个词）
    
    Args:
        file_path: 词库文件路径
        
    Returns:
        词条列表
    """
    words = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    words.append(line)
    except FileNotFoundError:
        pass
    return words


def load_forbidden_words() -> List[str]:
    """加载禁用词库"""
    return load_word_list(config.FORBIDDEN_WORDS_FILE)


def load_colloquial_words() -> List[str]:
    """加载口语化词库"""
    return load_word_list(config.COLLOQUIAL_WORDS_FILE)


def load_research_directions() -> List[str]:
    """加载研究方向列表"""
    return load_word_list(config.RESEARCH_DIRECTIONS_FILE)


# ============================================================================
# 规则匹配辅助函数
# ============================================================================

def check_value_in_range(actual: float, expected: float, tolerance: float = 0,
                         compare: str = 'equals') -> bool:
    """
    检查数值是否在允许范围内
    
    Args:
        actual: 实际值
        expected: 期望值
        tolerance: 允许误差
        compare: 比较方式 ('equals', 'gte', 'lte', 'gt', 'lt')
        
    Returns:
        是否通过检查
    """
    if compare == 'equals':
        return abs(actual - expected) <= tolerance
    elif compare == 'gte':
        return actual >= expected - tolerance
    elif compare == 'lte':
        return actual <= expected + tolerance
    elif compare == 'gt':
        return actual > expected - tolerance
    elif compare == 'lt':
        return actual < expected + tolerance
    return False


def normalize_text(text: str) -> str:
    """文本规范化（去除首尾空白、统一空格）"""
    if not text:
        return ''
    # 替换多个空白字符为单个空格
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# ============================================================================
# 文档解析辅助函数
# ============================================================================

def get_paragraph_text(para) -> str:
    """安全获取段落文本"""
    try:
        return para.text if para else ''
    except Exception:
        return ''


def get_run_text(run) -> str:
    """安全获取 run 文本"""
    try:
        return run.text if run else ''
    except Exception:
        return ''


def iter_paragraph_runs(para):
    """
    遍历段落中的所有 runs
    
    Yields:
        (run, run_text) 元组
    """
    try:
        for run in para.runs:
            yield run, get_run_text(run)
    except Exception:
        pass


def is_paragraph_empty(para) -> bool:
    """判断段落是否为空"""
    try:
        return not para.text.strip() if para else True
    except Exception:
        return True


def has_style(para, style_name: str) -> bool:
    """检查段落是否具有指定样式"""
    try:
        if para.style and para.style.name:
            return style_name in para.style.name
        return False
    except Exception:
        return False
