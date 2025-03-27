#!/usr/bin/env python3
"""内容生产控制器比较程序

该脚本提供命令行界面，用于比较不同的内容生产控制器实现。
"""

import argparse
import asyncio
import logging
import sys
import os
from datetime import datetime

from controller_benchmark import ControllerBenchmark

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)

logger = logging.getLogger(__name__)

async def run_benchmark(args):
    """运行基准测试

    Args:
        args: 命令行参数
    """
    # 创建基准测试实例
    benchmark = ControllerBenchmark(model_name=args.model)

    # 解析控制器类型
    controller_types = args.controllers.split(',') if args.controllers else None

    # 初始化控制器
    logger.info(f"初始化控制器: {controller_types or '所有'}")
    await benchmark.initialize_controllers(controller_types)

    # 运行基准测试
    logger.info(f"开始基准测试 - 类别: {args.category}, 风格: {args.style}")
    result = await benchmark.run_benchmark(
        category=args.category,
        style=args.style,
        controller_types=controller_types
    )

    # 生成报告
    report_path = args.output or f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report = benchmark.generate_report(report_path)

    logger.info(f"基准测试完成, 报告已保存至: {report_path}")

    if args.verbose:
        print("\n" + "="*50)
        print("比较报告概要:")
        print("="*50)

        # 打印报告前10行和最后10行
        report_lines = report.split('\n')
        header = '\n'.join(report_lines[:10])
        footer = '\n'.join(report_lines[-10:]) if len(report_lines) > 20 else ''

        print(header)
        if footer:
            print("...\n" + footer)

        print(f"\n完整报告请查看: {report_path}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="比较不同的内容生产控制器实现")

    parser.add_argument(
        "--category",
        type=str,
        default="人工智能",
        help="内容类别，例如：'人工智能'"
    )

    parser.add_argument(
        "--style",
        type=str,
        default="科技",
        help="写作风格，例如：'科技'"
    )

    parser.add_argument(
        "--controllers",
        type=str,
        help="要比较的控制器类型，以逗号分隔，例如：'custom_sequential,crewai_manager'"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4",
        help="使用的LLM模型，例如：'gpt-4'"
    )

    parser.add_argument(
        "--output",
        type=str,
        help="报告输出文件路径"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细输出"
    )

    args = parser.parse_args()

    try:
        asyncio.run(run_benchmark(args))
    except KeyboardInterrupt:
        logger.info("用户中断，正在退出...")
        sys.exit(1)
    except Exception as e:
        logger.error(f"运行基准测试失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
