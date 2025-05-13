#!/usr/bin/env python
"""
运行所有API单元测试的脚本
"""
import pytest
import os
import sys

# 确保可以导入项目模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == "__main__":
    # 默认运行tests目录下的所有测试
    test_args = ["--verbose", "--asyncio-mode=auto", "tests/"]
    
    # 添加覆盖率报告
    test_args.extend(["--cov=api", "--cov-report", "term-missing"])
    
    # 运行测试
    exit_code = pytest.main(test_args)
    
    # 返回测试结果码
    sys.exit(exit_code) 