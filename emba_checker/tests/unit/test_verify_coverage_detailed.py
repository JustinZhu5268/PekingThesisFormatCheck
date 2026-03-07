# -*- coding: utf-8 -*-
"""
test_verify_coverage_detailed.py - verify_coverage详细单元测试 (简化版)
目标：行覆盖>=50%, 深度>=25%
"""
import pytest
import sys
import os
import tempfile
import json

sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')


@pytest.mark.unit
class TestParseMdKeys:
    """parse_md_keys函数测试"""

    def test_parse_md_keys_basic(self):
        from emba_checker.verify_coverage import parse_md_keys
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write("# 标题\n\n|要素|format|紧急程度|可编程性|检测|\n|---|---|---|---|---|---|\n|测试|格式|★★★★★|✅|检测方法|")
            temp_path = f.name
        try:
            keys = parse_md_keys(temp_path)
            assert isinstance(keys, set)
        finally:
            os.unlink(temp_path)

    def test_parse_md_keys_empty(self):
        from emba_checker.verify_coverage import parse_md_keys
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write("")
            temp_path = f.name
        try:
            keys = parse_md_keys(temp_path)
            assert keys == set()
        finally:
            os.unlink(temp_path)

    def test_parse_md_keys_no_tables(self):
        from emba_checker.verify_coverage import parse_md_keys
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write("# 标题\n\n普通文本")
            temp_path = f.name
        try:
            keys = parse_md_keys(temp_path)
            assert keys == set()
        finally:
            os.unlink(temp_path)


@pytest.mark.unit
class TestParseRegistryKeys:
    """parse_registry_keys函数测试"""

    def test_parse_registry_keys_basic(self):
        from emba_checker.verify_coverage import parse_registry_keys
        rules = [{"rule_id": "T1", "md_source_key": "章节::要素"}]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(rules, f)
            temp_path = f.name
        try:
            keys = parse_registry_keys(temp_path)
            assert "章节::要素" in keys
        finally:
            os.unlink(temp_path)

    def test_parse_registry_keys_empty(self):
        from emba_checker.verify_coverage import parse_registry_keys
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump([], f)
            temp_path = f.name
        try:
            keys = parse_registry_keys(temp_path)
            assert keys == set()
        finally:
            os.unlink(temp_path)
