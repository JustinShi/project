"""
测试运行器
"""
import pytest
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_tests():
    """运行所有测试"""
    # 测试配置
    test_args = [
        "tests/",  # 测试目录
        "-v",      # 详细输出
        "--tb=short",  # 简短的traceback
        "--strict-markers",  # 严格的标记
        "--disable-warnings",  # 禁用警告
        "--color=yes",  # 彩色输出
        "-x",      # 遇到第一个失败就停止
    ]
    
    # 运行测试
    exit_code = pytest.main(test_args)
    return exit_code

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
