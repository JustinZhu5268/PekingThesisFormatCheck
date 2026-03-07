# -*- coding: utf-8 -*-
"""
test_config_extended.py - config模块测试
"""
import pytest
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

from emba_checker import config

@pytest.mark.unit
class TestConfigConstants:
    """测试config模块的常量"""

    def test_font_size_map(self):
        """测试字号映射"""
        assert "一号" in config.FONT_SIZE_MAP
        assert config.FONT_SIZE_MAP["一号"] == 26
        
    def test_zones(self):
        """测试zone定义"""
        assert "cover" in config.ZONES
        assert "body_chapter" in config.ZONES
        
    def test_groups(self):
        """测试group定义"""
        assert "Group1_Global" in config.GROUPS
        assert "Group2_Paragraphs" in config.GROUPS
        
    def test_check_types(self):
        """测试check_type定义"""
        assert "paragraph_style" in config.CHECK_TYPES
        assert "regex_match" in config.CHECK_TYPES
        
    def test_alignment_map(self):
        """测试对齐映射"""
        assert "LEFT" in config.ALIGNMENT_MAP
        assert "CENTER" in config.ALIGNMENT_MAP
        
    def test_default_page_margins(self):
        """测试默认页边距"""
        assert config.DEFAULT_PAGE_MARGINS is not None
        assert "top" in config.DEFAULT_PAGE_MARGINS
        
    def test_default_page_size(self):
        """测试默认页面大小"""
        assert config.DEFAULT_PAGE_SIZE is not None
        assert "width" in config.DEFAULT_PAGE_SIZE
        
    def test_chinese_punctuation(self):
        """测试中文标点"""
        assert "，" in config.CHINESE_PUNCTUATION
        
    def test_english_punctuation(self):
        """测试英文标点"""
        assert "," in config.ENGLISH_PUNCTUATION
        
    def test_regex_patterns(self):
        """测试正则模式"""
        assert config.REGEX_PATTERNS is not None
        assert "chinese_date" in config.REGEX_PATTERNS
