#!/usr/bin/env python3
"""风格团队独立运行脚本

该脚本提供了独立运行风格团队的功能，用于测试或单独使用风格适配功能。
"""

import os
import sys
import json
import asyncio
import logging
import argparse
import glob
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from core.agents.style_crew import StyleCrew
from core.models.article import Article
from core.models.platform import Platform
from core.constants.style_types import get_platform_style_type, get_style_features, get_style_description

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("StyleCrew")

def load_platform_from_file(file_path):
    """从文件加载平台配置

    Args:
        file_path: 平台配置JSON文件路径

    Returns:
        Platform对象
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            platform_data = json.load(f)
        return Platform(**platform_data)
    except Exception as e:
        logger.error(f"加载平台配置失败: {str(e)}")
        return None

def get_platform_by_name(platform_name):
    """根据平台名称获取平台配置

    Args:
        platform_name: 平台名称

    Returns:
        Platform对象，如未找到则返回None
    """
    platforms_dir = Path(__file__).parent / "platforms"
    platform_files = glob.glob(str(platforms_dir / "*.json"))

    for file_path in platform_files:
        platform = load_platform_from_file(file_path)
        if platform and (platform.id == platform_name or platform.name == platform_name):
            return platform

    return None

def get_default_platform():
    """获取默认平台配置（默认使用第一个找到的平台）

    Returns:
        Platform对象
    """
    platforms_dir = Path(__file__).parent.parent.parent / "constants" / "platforms"
    platform_files = glob.glob(str(platforms_dir / "*.json"))

    if platform_files:
        return load_platform_from_file(platform_files[0])

    # 如果没有找到平台配置，使用示例平台作为后备
    example_platform_path = Path(__file__).parent / "example_platform.json"
    if example_platform_path.exists():
        return load_platform_from_file(example_platform_path)

    logger.error("未找到任何平台配置文件")
    return None

def list_available_platforms():
    """列出所有可用的平台

    Returns:
        平台列表，每个元素为(id, name)元组
    """
    platforms_dir = Path(__file__).parent / "platforms"
    platform_files = glob.glob(str(platforms_dir / "*.json"))
    platforms = []

    for file_path in platform_files:
        platform = load_platform_from_file(file_path)
        if platform:
            platforms.append((platform.id, platform.name))

    return platforms

async def run_style_adaptation(input_file: str,
                              output_file: str,
                              platform_name: str = None,
                              verbose: bool = False,
                              list_platforms: bool = False):
    """运行风格适配流程

    Args:
        input_file: 输入文章JSON文件路径
        output_file: 输出结果JSON文件路径
        platform_name: 目标平台名称，如不提供则使用默认平台
        verbose: 是否显示详细日志
        list_platforms: 是否只列出可用平台
    """
    if verbose:
        logger.setLevel(logging.DEBUG)

    # 列出可用平台
    if list_platforms:
        platforms = list_available_platforms()
        if not platforms:
            logger.info("未找到任何平台配置")
            return

        logger.info("可用平台列表:")
        for idx, (platform_id, platform_name) in enumerate(platforms, 1):
            logger.info(f"{idx}. {platform_name} (ID: {platform_id})")
        return

    logger.info(f"正在加载输入文件: {input_file}")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            article_data = json.load(f)
    except Exception as e:
        logger.error(f"加载输入文件失败: {str(e)}")
        return

    # 创建文章对象
    article = Article.from_dict(article_data)
    logger.info(f"成功加载文章《{article.title}》，字数: {article.word_count}")

    # 获取目标平台
    platform = None
    if platform_name:
        platform = get_platform_by_name(platform_name)
        if not platform:
            logger.warning(f"未找到平台 '{platform_name}'，使用默认平台")
            platform = get_default_platform()
    else:
        platform = get_default_platform()

    if not platform:
        logger.error("无法获取平台配置，请确保platforms目录中有有效的平台配置文件")
        return

    # 获取预定义风格信息
    platform_style_type = get_platform_style_type(platform.id)
    if platform_style_type:
        style_features = get_style_features(platform_style_type)
        style_description = get_style_description(platform_style_type)
        logger.info(f"目标平台: {platform.name}, 预定义风格: {platform_style_type}")
        logger.info(f"风格描述: {style_description}")
    else:
        logger.info(f"目标平台: {platform.name}, 无预定义风格")

    # 创建风格团队
    style_crew = StyleCrew()
    style_crew.initialize(platform)

    # 执行风格适配
    logger.info("开始执行风格适配...")
    try:
        result = await style_crew.adapt_style(article, platform)

        # 输出结果
        logger.info("风格适配完成，正在保存结果...")
        output_data = {
            "article": result.final_article.to_dict(),
            "platform": platform.name,
            "platform_analysis": result.platform_analysis,
            "style_recommendations": result.style_recommendations,
            "quality_check": result.quality_check,
            "execution_time": result.execution_time
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        logger.info(f"结果已保存到: {output_file}")
        logger.info(f"执行时间: {result.execution_time:.2f}秒")

        # 显示质量检查结果
        if result.quality_check:
            if "overall_score" in result.quality_check:
                logger.info(f"质量评分: {result.quality_check['overall_score']}/10")
            if "issues" in result.quality_check:
                issues_count = len(result.quality_check["issues"])
                logger.info(f"发现问题: {issues_count}个")

            if verbose and "issues" in result.quality_check:
                for i, issue in enumerate(result.quality_check["issues"], 1):
                    logger.debug(f"问题 {i}: {issue.get('description', '未知问题')}")

    except Exception as e:
        logger.error(f"风格适配过程出错: {str(e)}")
        raise

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="风格团队独立运行工具")
    parser.add_argument("input", help="输入文章JSON文件路径", nargs="?")
    parser.add_argument("output", help="输出结果JSON文件路径", nargs="?")
    parser.add_argument("--platform", "-p", help="目标平台名称")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有可用平台")

    args = parser.parse_args()

    if args.list:
        asyncio.run(run_style_adaptation(
            input_file="",
            output_file="",
            list_platforms=True
        ))
        return

    if not args.input or not args.output:
        parser.print_help()
        return

    asyncio.run(run_style_adaptation(
        input_file=args.input,
        output_file=args.output,
        platform_name=args.platform,
        verbose=args.verbose
    ))

if __name__ == "__main__":
    main()
