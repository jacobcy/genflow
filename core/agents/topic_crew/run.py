#!/usr/bin/env python
"""
话题团队运行脚本

这个脚本可以从项目根目录直接运行，简化了使用流程。
用法：python -m core.agents.topic_crew.run
"""
import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, project_root)

# 导入必要的模块
from core.agents.topic_crew.topic_crew import TopicCrew
from core.config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("topic_crew")

async def run_topic_discovery(category=None, count=3, verbose=False):
    """运行话题发现流程"""
    logger.info(f"初始化配置和团队...")
    config = Config()
    crew = TopicCrew(config=config)

    logger.info(f"开始发现{category or '所有领域'}的热门话题...")
    topics = await crew.discover_topics(category=category, count=count)

    logger.info(f"\n发现了 {len(topics)} 个话题\n")
    for topic in topics:
        logger.info(f"- {topic.title}: {topic.description}")
        if verbose:
            logger.info(f"  分类: {topic.category}")
            logger.info(f"  标签: {', '.join(topic.tags)}")
            logger.info(f"  搜索量: {topic.metrics.search_volume}")
            logger.info(f"  趋势分数: {topic.metrics.trend_score:.2f}")

    return topics

async def run_full_workflow(category=None, count=3, verbose=False):
    """运行完整工作流程"""
    logger.info(f"初始化配置和团队...")
    config = Config()
    crew = TopicCrew(config=config)

    logger.info(f"开始执行完整话题工作流...")
    result = await crew.run_full_workflow(category=category, count=count)

    logger.info(f"\n完成! 总共发现 {result['total_topics']} 个话题，其中 {result['approved_topics']} 个获批")

    # 保存结果
    output_dir = Path(project_root) / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "topic_analysis_result.json"

    import json
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    logger.info(f"结果已保存到 {output_file}")
    return result

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='选题团队工作流')
    parser.add_argument('--mode', type=str, default='discover', choices=['discover', 'full'],
                        help='运行模式: discover(仅发现) 或 full(完整流程)')
    parser.add_argument('--category', type=str, default=None,
                        help='话题分类, 例如: 科技, 教育, 娱乐等')
    parser.add_argument('--count', type=int, default=3,
                        help='需要发现的话题数量')
    parser.add_argument('--verbose', action='store_true',
                        help='是否显示详细信息')

    args = parser.parse_args()

    logger.info(f"开始运行选题团队，模式: {args.mode}")
    try:
        if args.mode == 'discover':
            await run_topic_discovery(args.category, args.count, args.verbose)
        else:
            await run_full_workflow(args.category, args.count, args.verbose)
        logger.info("运行完成")
    except Exception as e:
        logger.error(f"运行过程中出错: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
