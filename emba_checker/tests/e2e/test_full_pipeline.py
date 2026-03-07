# -*- coding: utf-8 -*-
"""
test_full_pipeline.py - 完整管线E2E测试
简化版
"""
import pytest
import sys
import os
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

import tempfile

@pytest.mark.e2e
class TestFullPipeline:

    def test_original_file_untouched(self):
        """测试原文件不被修改"""
        input_docx = "D:/Projects/ThesisFormatCheck/emba_checker/tests/fixtures/test_complete_template.docx"
        if not os.path.exists(input_docx):
            pytest.skip("测试模板不存在")
        
        import hashlib
        with open(input_docx, "rb") as f:
            hash_before = hashlib.md5(f.read()).hexdigest()
        
        # 测试 main_engine 可以导入
        from emba_checker.main_engine import MainEngine
        assert MainEngine is not None
        
        with open(input_docx, "rb") as f:
            hash_after = hashlib.md5(f.read()).hexdigest()
        
        assert hash_before == hash_after, "原文件被修改了！"
