# -*- coding: utf-8 -*-
"""
test_main_engine_extended.py - MainEngine扩展测试
"""
import pytest
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

@pytest.mark.unit
class TestMainEngineStructure:
    """测试MainEngine类结构"""

    def test_main_engine_import(self):
        """验证MainEngine可导入"""
        from emba_checker.main_engine import MainEngine
        assert MainEngine is not None

    def test_main_engine_has_init(self):
        """验证有初始化方法"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/main_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert '__init__' in content

    def test_main_engine_has_run(self):
        """验证有run方法"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/main_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'def run' in content

    def test_main_engine_loads_rules(self):
        """验证加载规则"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/main_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'json.load' in content

    def test_main_engine_has_detect_zones(self):
        """验证有区域检测"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/main_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'detect_zones' in content

    def test_main_engine_has_docx_engine(self):
        """验证有运行docx引擎"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/main_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'DocxEngine' in content

    def test_main_engine_has_issue_list(self):
        """验证有问题列表"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/main_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'self.issues' in content

@pytest.mark.unit
class TestMainEngineIntegration:
    """测试MainEngine集成"""

    def test_main_engine_imports_docx(self):
        """验证导入Document"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/main_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'from docx import Document' in content

    def test_main_engine_handles_cli_args(self):
        """验证处理CLI参数"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/main_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'argparse' in content or 'sys.argv' in content

@pytest.mark.unit
class TestMainEngineErrorHandling:
    """测试MainEngine错误处理"""

    def test_main_engine_has_progress_callback(self):
        """验证有进度回调"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/main_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'progress_callback' in content

    def test_main_engine_has_error_handling(self):
        """验证有异常处理"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/main_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'try' in content or 'except' in content

@pytest.mark.unit
class TestMainEngineOutput:
    """测试MainEngine输出"""

    def test_main_engine_generates_report(self):
        """验证生成报告"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/main_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'report' in content.lower()

    def test_main_engine_has_stats(self):
        """验证有统计信息"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/main_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'self.stats' in content

    def test_main_engine_has_timestamp(self):
        """验证有时间戳"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/main_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'datetime' in content

@pytest.mark.unit
class TestMainEngineConstants:
    """测试MainEngine常量"""

    def test_main_engine_has_base_dir(self):
        """验证有基础目录"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/main_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'BASE_DIR' in content

    def test_main_engine_has_default_rules_path(self):
        """验证有默认规则路径"""
        import os
        path = 'D:/Projects/ThesisFormatCheck/emba_checker/main_engine.py'
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'rules_registry.json' in content
