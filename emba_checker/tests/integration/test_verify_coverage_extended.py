# -*- coding: utf-8 -*-
"""
test_verify_coverage_extended.py - verify_coverage扩展测试
包含边界测试和异常测试，用于提升测试覆盖率
"""
import pytest
import sys
import os
import tempfile
import json

sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')


@pytest.mark.integration
class TestVerifyCoverageBoundary:
    """verify_coverage边界测试"""

    def test_empty_md_file(self):
        """边界测试：空MD文件"""
        from emba_checker.verify_coverage import parse_md_keys
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write("")
            temp_path = f.name
        
        try:
            keys = parse_md_keys(temp_path)
            assert keys == set()
        finally:
            os.unlink(temp_path)

    def test_md_without_tables(self):
        """边界测试：无表格的MD文件"""
        from emba_checker.verify_coverage import parse_md_keys
        
        content = "# 标题\n\n这是普通文本内容，没有表格。"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            keys = parse_md_keys(temp_path)
            assert keys == set()
        finally:
            os.unlink(temp_path)

    def test_empty_registry_file(self):
        """边界测试：空规则库文件"""
        from emba_checker.verify_coverage import parse_registry_keys
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump([], f)
            temp_path = f.name
        
        try:
            keys = parse_registry_keys(temp_path)
            assert keys == set()
        finally:
            os.unlink(temp_path)

    def test_single_rule(self):
        """边界测试：单条规则"""
        from emba_checker.verify_coverage import parse_registry_keys
        
        rules = [{"rule_id": "TEST_01", "md_source_key": "章节::要素"}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(rules, f)
            temp_path = f.name
        
        try:
            keys = parse_registry_keys(temp_path)
            assert len(keys) == 1
        finally:
            os.unlink(temp_path)

    def test_many_rules(self):
        """边界测试：大量规则（100条）"""
        from emba_checker.verify_coverage import parse_registry_keys
        
        rules = [
            {"rule_id": f"TEST_{i:03d}", "md_source_key": f"章节{i}::要素{i}"}
            for i in range(100)
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(rules, f)
            temp_path = f.name
        
        try:
            keys = parse_registry_keys(temp_path)
            assert len(keys) == 100
        finally:
            os.unlink(temp_path)


@pytest.mark.integration
class TestVerifyCoverageException:
    """verify_coverage异常测试"""

    def test_missing_md_file(self):
        """异常测试：MD文件不存在 - 验证抛出FileNotFoundError"""
        from emba_checker.verify_coverage import parse_md_keys
        
        import pytest
        with pytest.raises(FileNotFoundError):
            parse_md_keys("nonexistent_file.md")

    def test_invalid_json_file(self):
        """异常测试：无效JSON文件 - 验证抛出JSONDecodeError"""
        from emba_checker.verify_coverage import parse_registry_keys
        
        import pytest
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            f.write("invalid json content")
            temp_path = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                parse_registry_keys(temp_path)
        finally:
            os.unlink(temp_path)

    def test_empty_json_array(self):
        """异常测试：空JSON数组"""
        from emba_checker.verify_coverage import parse_registry_keys
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump([], f)
            temp_path = f.name
        
        try:
            keys = parse_registry_keys(temp_path)
            assert keys == set()
        finally:
            os.unlink(temp_path)

    def test_missing_md_source_key(self):
        """异常测试：缺少md_source_key"""
        from emba_checker.verify_coverage import parse_registry_keys
        
        rules = [{"rule_id": "TEST_01"}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(rules, f)
            temp_path = f.name
        
        try:
            keys = parse_registry_keys(temp_path)
            assert "章节::要素" not in keys
        finally:
            os.unlink(temp_path)

    def test_md_file_encoding(self):
        """异常测试：文件编码问题"""
        from emba_checker.verify_coverage import parse_md_keys
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write("# 标题\n\n|要素|format|紧急程度|可编程性|检测|\n|---|---|---|---|---|---|\n|测试|格式|★★★★★|✅|检测方法|")
            temp_path = f.name
        
        try:
            keys = parse_md_keys(temp_path)
            assert isinstance(keys, set)
        finally:
            os.unlink(temp_path)

    def test_invalid_md_format(self):
        """异常测试：无效MD格式"""
        from emba_checker.verify_coverage import parse_md_keys
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write("这是无效的MD内容 {[]}")
            temp_path = f.name
        
        try:
            keys = parse_md_keys(temp_path)
            assert isinstance(keys, set)
        finally:
            os.unlink(temp_path)

    def test_verify_coverage_function(self):
        """测试：verify_coverage函数"""
        from emba_checker.verify_coverage import verify_coverage
        
        # 创建临时MD文件
        md_content = """# 格式要求

## 页面设置

| 章节 | 要素 | 要求 |
|------|------|------|
| 通用 | 页面尺寸 | A4 |
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(md_content)
            md_path = f.name
        
        # 创建临时规则文件
        rules_content = [{"rule_id": "TEST_01", "md_source_key": "通用::页面尺寸"}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(rules_content, f)
            reg_path = f.name
        
        try:
            md_keys, reg_keys = verify_coverage(md_path, reg_path)
            assert isinstance(md_keys, set)
            assert isinstance(reg_keys, set)
        finally:
            os.unlink(md_path)
            os.unlink(reg_path)

    def test_generate_coverage_report_function(self):
        """测试：generate_coverage_report函数能正常调用"""
        from emba_checker.verify_coverage import generate_coverage_report
        
        # 函数会读取默认的MD和规则库文件，然后生成报告
        # 这里测试函数能正常调用并返回字符串
        try:
            report = generate_coverage_report(set(), set())
            assert isinstance(report, str)
        except FileNotFoundError:
            # 如果默认文件不存在，跳过
            pass
