#!/usr/bin/env python
"""
ResearchCrew测试运行脚本

提供命令行界面运行ResearchCrew模块的测试。
支持运行所有测试或特定测试方法。
"""

import os
import sys
import pytest
import logging
import argparse

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def configure_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('research_crew_test.log')
        ]
    )

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='运行ResearchCrew模块测试')
    parser.add_argument('--test-class', choices=['all', 'config', 'crew', 'comprehensive'],
                        default='all', help='要测试的类 (config: 配置, crew: 基本功能, comprehensive: 综合功能)')
    parser.add_argument('--test-method', type=str,
                        help='指定要测试的方法名称，例如：test_research_topic_string')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细输出')
    args = parser.parse_args()

    # 配置日志
    configure_logging()

    # 测试文件（使用当前目录中的文件）
    test_file = 'test_research_crew.py'

    # 类名映射
    class_names = {
        'config': 'TestResearchConfig',
        'crew': 'TestResearchCrew',
        'comprehensive': 'TestResearchCrewComprehensive'
    }

    # 构建pytest参数
    pytest_args = ['-xvs' if args.verbose else '-xs']

    if args.test_class == 'all':
        # 测试所有类
        pytest_args.append(test_file)
    else:
        # 测试特定类
        class_name = class_names[args.test_class]
        if args.test_method:
            # 测试特定方法
            pytest_args.append(f"{test_file}::{class_name}::{args.test_method}")
        else:
            # 测试类所有方法
            pytest_args.append(f"{test_file}::{class_name}")

    logging.info(f"开始运行ResearchCrew测试: 类={args.test_class}, 方法={args.test_method or '所有'}")

    # 运行测试
    result = pytest.main(pytest_args)

    if result == 0:
        logging.info("测试成功完成")
    else:
        logging.error(f"测试失败，返回码: {result}")

    return result

if __name__ == "__main__":
    sys.exit(main())
