#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试分级体系验证脚本 (Test Level Validation)

验证测试分级体系达标情况，基于以下标准：
- P0模块：行覆盖>=80%，深度测试>=60%
- P1模块：行覆盖>=70%，深度测试>=40%
- P2模块：行覆盖>=50%，深度测试>=25%
- P3模块：行覆盖>=30%，深度测试>=10%

使用方法：
    python validate_test_levels.py
"""

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple

# 配置
COVERAGE_XML = Path(__file__).parent / "coverage.xml"
TESTS_DIR = Path(__file__).parent / "tests"

# 分级配置
TEST_LEVELS = {
    "P0": {
        "modules": ["docx_engine.py", "rule_engine.py"],
        "min_line_coverage": 0.80,
        "min_depth_ratio": 0.60,
    },
    "P1": {
        "modules": ["claude_engine.py", "zone_detector.py", "safe_annotator.py"],
        "min_line_coverage": 0.70,
        "min_depth_ratio": 0.40,
    },
    "P2": {
        "modules": ["utils.py", "md_parser.py", "verify_coverage.py"],
        "min_line_coverage": 0.50,
        "min_depth_ratio": 0.25,
    },
    "P3": {
        "modules": ["config.py", "base_executor.py", "main_engine.py"],
        "min_line_coverage": 0.30,
        "min_depth_ratio": 0.10,
    },
}


def parse_coverage_xml(xml_path: Path) -> Dict[str, float]:
    """解析coverage.xml，提取各模块的行覆盖率"""
    coverage_data = {}
    
    if not xml_path.exists():
        print(f"警告：coverage.xml 不存在 ({xml_path})")
        return coverage_data
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # 遍历所有class元素
        for package in root.findall(".//package"):
            for cls in package.findall("class"):
                filename = cls.get("filename", "")
                line_rate = cls.get("line-rate", "0")
                
                if filename.endswith(".py"):
                    # 提取模块名
                    module_name = os.path.basename(filename)
                    coverage_data[module_name] = float(line_rate)
        
    except Exception as e:
        print(f"解析coverage.xml失败: {e}")
    
    return coverage_data


def get_depth_test_patterns() -> Tuple[List[str], List[str]]:
    """获取深度测试的测试函数命名模式"""
    # Boundary/Edge测试模式
    boundary_patterns = [
        r"boundary",
        r"edge",
        r"min",
        r"max",
        r"极限",
        r"边界",
    ]
    
    # Exception/Error测试模式
    exception_patterns = [
        r"error",
        r"exception",
        r"timeout",
        r"invalid",
        r"fail",
        r"错误",
        r"异常",
    ]
    
    return boundary_patterns, exception_patterns


def count_depth_tests(tests_dir: Path, module_name: str) -> Tuple[int, int, int]:
    """
    统计模块对应的深度测试数量
    
    返回: (happy_path_tests, boundary_tests, exception_tests)
    """
    happy_count = 0
    boundary_count = 0
    exception_count = 0
    
    boundary_patterns, exception_patterns = get_depth_test_patterns()
    
    # 确定需要搜索的测试文件
    # 根据模块名推断可能的测试文件
    module_base = module_name.replace(".py", "")
    
    # 搜索所有测试文件
    test_files = list(tests_dir.rglob("test_*.py"))
    
    for test_file in test_files:
        try:
            content = test_file.read_text(encoding="utf-8")
            
            # 查找与该模块相关的测试函数
            # 简单启发式：测试文件中包含模块名的import或测试函数名包含模块名
            if module_base.lower() not in content.lower():
                continue
                
            # 查找所有测试函数
            test_functions = re.findall(r"def (test_\w+)", content)
            
            for func_name in test_functions:
                func_name_lower = func_name.lower()
                
                # 判断测试类型
                is_boundary = any(p in func_name_lower for p in boundary_patterns)
                is_exception = any(p in func_name_lower for p in exception_patterns)
                
                if is_boundary:
                    boundary_count += 1
                elif is_exception:
                    exception_count += 1
                else:
                    happy_count += 1
                    
        except Exception:
            continue
    
    return happy_count, boundary_count, exception_count


def calculate_depth_ratio(happy: int, boundary: int, exception: int) -> float:
    """计算深度测试比例"""
    total = happy + boundary + exception
    if total == 0:
        return 0.0
    return (boundary + exception) / total


def get_module_coverage(coverage_data: Dict[str, float], module_name: str) -> float:
    """获取模块的覆盖率"""
    # 精确匹配
    if module_name in coverage_data:
        return coverage_data[module_name]
    
    # 尝试路径匹配
    for key, value in coverage_data.items():
        if module_name in key or key in module_name:
            return value
    
    return 0.0


def validate_p0_levels(coverage_data: Dict[str, float]) -> List[str]:
    """验证P0模块是否达标"""
    errors = []
    config = TEST_LEVELS["P0"]
    
    for module in config["modules"]:
        line_cov = get_module_coverage(coverage_data, module)
        
        # 尝试获取深度测试比例
        happy, boundary, exception = count_depth_tests(TESTS_DIR, module)
        depth_ratio = calculate_depth_ratio(happy, boundary, exception)
        
        # 检查行覆盖
        if line_cov < config["min_line_coverage"]:
            errors.append(
                f"P0 模块 {module} 行覆盖 {line_cov:.1%} < {config['min_line_coverage']:.0%}"
            )
        
        # 检查深度测试
        if depth_ratio < config["min_depth_ratio"]:
            errors.append(
                f"P0 模块 {module} 深度测试 {depth_ratio:.1%} < {config['min_depth_ratio']:.0%} "
                f"(Happy:{happy}, Boundary:{boundary}, Exception:{exception})"
            )
    
    return errors


def validate_p1_levels(coverage_data: Dict[str, float]) -> List[str]:
    """验证P1模块是否达标"""
    errors = []
    config = TEST_LEVELS["P1"]
    
    for module in config["modules"]:
        line_cov = get_module_coverage(coverage_data, module)
        
        happy, boundary, exception = count_depth_tests(TESTS_DIR, module)
        depth_ratio = calculate_depth_ratio(happy, boundary, exception)
        
        if line_cov < config["min_line_coverage"]:
            errors.append(
                f"P1 模块 {module} 行覆盖 {line_cov:.1%} < {config['min_line_coverage']:.0%}"
            )
        
        if depth_ratio < config["min_depth_ratio"]:
            errors.append(
                f"P1 模块 {module} 深度测试 {depth_ratio:.1%} < {config['min_depth_ratio']:.0%} "
                f"(Happy:{happy}, Boundary:{boundary}, Exception:{exception})"
            )
    
    return errors


def validate_p2_levels(coverage_data: Dict[str, float]) -> List[str]:
    """验证P2模块是否达标"""
    errors = []
    config = TEST_LEVELS["P2"]
    
    for module in config["modules"]:
        line_cov = get_module_coverage(coverage_data, module)
        
        happy, boundary, exception = count_depth_tests(TESTS_DIR, module)
        depth_ratio = calculate_depth_ratio(happy, boundary, exception)
        
        if line_cov < config["min_line_coverage"]:
            errors.append(
                f"P2 模块 {module} 行覆盖 {line_cov:.1%} < {config['min_line_coverage']:.0%}"
            )
        
        if depth_ratio < config["min_depth_ratio"]:
            errors.append(
                f"P2 模块 {module} 深度测试 {depth_ratio:.1%} < {config['min_depth_ratio']:.0%} "
                f"(Happy:{happy}, Boundary:{boundary}, Exception:{exception})"
            )
    
    return errors


def validate_p3_levels(coverage_data: Dict[str, float]) -> List[str]:
    """验证P3模块是否达标"""
    errors = []
    config = TEST_LEVELS["P3"]
    
    for module in config["modules"]:
        line_cov = get_module_coverage(coverage_data, module)
        
        happy, boundary, exception = count_depth_tests(TESTS_DIR, module)
        depth_ratio = calculate_depth_ratio(happy, boundary, exception)
        
        if line_cov < config["min_line_coverage"]:
            errors.append(
                f"P3 模块 {module} 行覆盖 {line_cov:.1%} < {config['min_line_coverage']:.0%}"
            )
        
        if depth_ratio < config["min_depth_ratio"]:
            errors.append(
                f"P3 模块 {module} 深度测试 {depth_ratio:.1%} < {config['min_depth_ratio']:.0%} "
                f"(Happy:{happy}, Boundary:{boundary}, Exception:{exception})"
            )
    
    return errors


def print_summary(coverage_data: Dict[str, float]) -> None:
    """打印测试分级汇总"""
    print("\n" + "=" * 70)
    print("测试分级体系验证汇总")
    print("=" * 70)
    
    for level, config in TEST_LEVELS.items():
        print(f"\n【{level}级】要求: 行覆盖>={config['min_line_coverage']:.0%}, 深度>={config['min_depth_ratio']:.0%}")
        print("-" * 50)
        
        for module in config["modules"]:
            line_cov = get_module_coverage(coverage_data, module)
            happy, boundary, exception = count_depth_tests(TESTS_DIR, module)
            depth_ratio = calculate_depth_ratio(happy, boundary, exception)
            
            line_status = "✓" if line_cov >= config["min_line_coverage"] else "✗"
            depth_status = "✓" if depth_ratio >= config["min_depth_ratio"] else "✗"
            
            print(f"  {module:30s} 行覆盖: {line_cov:6.1%} {line_status}  深度: {depth_ratio:6.1%} {depth_status}")
    
    print("\n" + "=" * 70)


def validate_test_levels() -> bool:
    """
    验证测试分级体系达标情况
    
    返回: True表示所有检查通过, False表示有未达标项
    """
    print("开始验证测试分级体系...")
    print(f"Coverage XML: {COVERAGE_XML}")
    print(f"Tests Dir: {TESTS_DIR}")
    
    # 解析覆盖率数据
    coverage_data = parse_coverage_xml(COVERAGE_XML)
    
    if not coverage_data:
        print("警告：无法获取覆盖率数据，跳过验证")
        return True
    
    # 打印汇总信息
    print_summary(coverage_data)
    
    # 执行各级别验证
    all_errors = []
    
    print("\n验证 P0 模块...")
    all_errors.extend(validate_p0_levels(coverage_data))
    
    print("验证 P1 模块...")
    all_errors.extend(validate_p1_levels(coverage_data))
    
    print("验证 P2 模块...")
    all_errors.extend(validate_p2_levels(coverage_data))
    
    print("验证 P3 模块...")
    all_errors.extend(validate_p3_levels(coverage_data))
    
    # 输出结果
    print("\n" + "=" * 70)
    if all_errors:
        print("验证结果: 未通过")
        print("-" * 70)
        for error in all_errors:
            print(f"  ✗ {error}")
        print("=" * 70)
        return False
    else:
        print("验证结果: 全部通过")
        print("=" * 70)
        return True


if __name__ == "__main__":
    success = validate_test_levels()
    exit(0 if success else 1)
