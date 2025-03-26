#!/usr/bin/env python
"""
选题工具测试运行脚本

简单的脚本，用于运行选题工具的测试用例。
用法: python tests/run_topic_tools_test.py
"""
import os
import sys
import logging
import pytest

# 设置日志级别
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

def main():
    """运行选题工具测试"""
    print("\n===== 开始运行选题工具测试 =====\n")
    
    # 构建测试文件路径
    test_file = os.path.join(current_dir, "test_topic_tools.py")
    
    # 运行测试
    exit_code = pytest.main([
        "-v",                # 详细输出
        "--log-cli-level=INFO",  # 控制台日志级别
        test_file            # 测试文件路径
    ])
    
    # 输出测试结果摘要
    if exit_code == 0:
        print("\n✅ 选题工具测试通过!")
    else:
        print("\n❌ 选题工具测试未通过!")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main()) 