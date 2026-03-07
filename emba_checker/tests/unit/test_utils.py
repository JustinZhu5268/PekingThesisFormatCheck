# -*- coding: utf-8 -*-
"""
test_utils.py - 工具函数测试
"""
import pytest
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

from emba_checker.utils import emu_to_cm, cm_to_emu, emu_to_pt, pt_to_emu, count_chinese_chars

@pytest.mark.unit
class TestUnitConversion:
    """单位换算函数测试"""

    @pytest.mark.parametrize("emu, expected_cm", [
        (360000, 1.0),
        (7200000, 20.0),
        (0, 0.0),
        (180000, 0.5),
    ])
    def test_emu_to_cm(self, emu, expected_cm):
        assert abs(emu_to_cm(emu) - expected_cm) < 0.001

    @pytest.mark.parametrize("cm, expected_emu", [
        (1.0, 360000),
        (2.54, 914400),
    ])
    def test_cm_to_emu(self, cm, expected_emu):
        assert cm_to_emu(cm) == expected_emu

    @pytest.mark.parametrize("emu, expected_pt", [
        (12700, 1.0),
        (152400, 12.0),  # 小四号
        (330200, 26.0),  # 一号
    ])
    def test_emu_to_pt(self, emu, expected_pt):
        assert abs(emu_to_pt(emu) - expected_pt) < 0.01


@pytest.mark.unit
class TestTextProcessing:
    """文本处理函数测试"""

    def test_count_chinese_chars(self):
        assert count_chinese_chars("这是一个测试") == 6
        assert count_chinese_chars("Hello World") == 0
        assert count_chinese_chars("测试测试") == 4
        assert count_chinese_chars("") == 0
