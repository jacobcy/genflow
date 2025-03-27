#!/usr/bin/env python
"""
CrewAI工具测试运行脚本

提供简单的命令行界面运行CrewAI工具测试。
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
            logging.FileHandler('crewai_tools_test.log')
        ]
    )

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='运行CrewAI工具测试')
    parser.add_argument('--team', choices=['all', 'research', 'review', 'topic', 'writing'],
                        default='all', help='要测试的团队工具模块')
    parser.add_argument('--tool', type=str, help='指定要测试的工具名称，例如：collect_content')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细输出')
    args = parser.parse_args()

    # 配置日志
    configure_logging()

    # 团队和测试文件映射
    team_files = {
        'research': 'tests/test_research_tools.py',
        'review': 'tests/test_review_tools.py',
        'topic': 'tests/test_topic_tools.py',
        'writing': 'tests/test_writing_tools.py'
    }

    # 构建pytest参数
    pytest_args = ['-xvs' if args.verbose else '-xs']

    if args.team == 'all':
        # 测试所有团队
        for file_path in team_files.values():
            pytest_args.append(file_path)
    else:
        # 测试特定团队
        file_path = team_files[args.team]
        if args.tool:
            # 测试特定工具
            function_name = f"test_{args.tool}_with_crewai"
            pytest_args.append(f"{file_path}::{function_name}")
        else:
            # 测试团队所有工具
            pytest_args.append(file_path)

    logging.info(f"开始运行CrewAI工具测试: 团队={args.team}, 工具={args.tool or '所有'}")

    # 运行测试
    result = pytest.main(pytest_args)

    if result == 0:
        logging.info("测试成功完成")
    else:
        logging.error(f"测试失败，返回码: {result}")

    return result

if __name__ == "__main__":
    sys.exit(main())
