#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""研究团队运行脚本

这个脚本提供命令行接口，用于运行研究团队的各种工作流程，包括：
- 单话题研究
- 完整研究工作流（研究+文章大纲）
- 批量话题研究

包含进度回调和结果存储功能。
"""
import os
import sys
import logging
import argparse
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from tqdm import tqdm

from core.agents.research_crew.research_crew import ResearchCrew
from core.config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('research_crew.log')
    ]
)
logger = logging.getLogger("research_run")

def configure_progress_bar(total_steps: int) -> tqdm:
    """配置进度条
    
    Args:
        total_steps: 总步骤数
        
    Returns:
        tqdm: 进度条对象
    """
    return tqdm(
        total=total_steps,
        desc="研究进度",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
    )

def progress_callback(progress_bar: tqdm) -> Callable:
    """创建进度回调函数
    
    Args:
        progress_bar: 进度条对象
        
    Returns:
        Callable: 回调函数
    """
    def callback(current_step: int, total_steps: int, step_name: str) -> None:
        """进度回调函数
        
        Args:
            current_step: 当前步骤
            total_steps: 总步骤数
            step_name: 步骤名称
        """
        progress_bar.total = total_steps
        progress_bar.set_description(f"研究进度 - {step_name}")
        progress_bar.update(1)
    
    return callback

def save_results(data: Any, output_dir: str, filename: str) -> str:
    """保存结果到文件
    
    Args:
        data: 要保存的数据
        output_dir: 输出目录
        filename: 文件名
        
    Returns:
        str: 保存的文件路径
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 准备文件路径
    file_path = os.path.join(output_dir, filename)
    
    # 保存数据
    if hasattr(data, 'to_dict'):
        # 如果对象有to_dict方法
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data.to_dict(), f, ensure_ascii=False, indent=2)
    elif hasattr(data, 'to_json'):
        # 如果对象有to_json方法
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data.to_json())
    else:
        # 尝试直接转换为JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"结果已保存到: {file_path}")
    return file_path

async def run_research(topic: str, output_dir: str, verbose: bool = False) -> str:
    """执行单个话题研究
    
    Args:
        topic: 研究话题
        output_dir: 输出目录
        verbose: 是否详细输出
        
    Returns:
        str: 结果文件路径
    """
    logger.info(f"开始研究话题: {topic}")
    
    # 创建配置
    config = Config()
    config.CREW_VERBOSE = verbose
    config.AGENT_VERBOSE = verbose
    
    # 创建研究团队
    crew = ResearchCrew(config=config)
    
    # 创建进度条
    progress_bar = configure_progress_bar(total_steps=4)
    
    # 执行研究
    result = crew.research_topic(
        topic=topic,
        progress_callback=progress_callback(progress_bar)
    )
    
    # 关闭进度条
    progress_bar.close()
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"research_{topic.replace(' ', '_')}_{timestamp}.json"
    result_path = save_results(result, output_dir, filename)
    
    logger.info(f"研究完成: {topic}")
    return result_path

async def run_full_workflow(topic: str, output_dir: str, verbose: bool = False) -> Dict[str, str]:
    """执行完整研究工作流
    
    Args:
        topic: 研究话题
        output_dir: 输出目录
        verbose: 是否详细输出
        
    Returns:
        Dict[str, str]: 结果文件路径字典
    """
    logger.info(f"开始完整研究工作流: {topic}")
    
    # 创建配置
    config = Config()
    config.CREW_VERBOSE = verbose
    config.AGENT_VERBOSE = verbose
    
    # 创建研究团队
    crew = ResearchCrew(config=config)
    
    # 创建进度条
    progress_bar = configure_progress_bar(total_steps=5)
    
    # 执行完整工作流
    research_result, article = crew.run_full_workflow(
        topic=topic,
        progress_callback=progress_callback(progress_bar)
    )
    
    # 关闭进度条
    progress_bar.close()
    
    # 生成时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    topic_slug = topic.replace(' ', '_')
    
    # 保存研究结果
    research_filename = f"research_{topic_slug}_{timestamp}.json"
    research_path = save_results(research_result, output_dir, research_filename)
    
    # 保存文章大纲
    article_filename = f"article_{topic_slug}_{timestamp}.json"
    article_path = save_results(article, output_dir, article_filename)
    
    # 获取并保存人类反馈（这里是模拟的）
    feedback = crew.get_human_feedback(research_result)
    feedback_filename = f"feedback_{topic_slug}_{timestamp}.json"
    feedback_path = save_results(feedback, output_dir, feedback_filename)
    
    # 保存工作流结果
    if crew.last_workflow_result:
        workflow_filename = f"workflow_{topic_slug}_{timestamp}.json"
        workflow_path = save_results(
            crew.last_workflow_result, 
            output_dir, 
            workflow_filename
        )
    else:
        workflow_path = None
    
    logger.info(f"完整研究工作流已完成: {topic}")
    
    return {
        "research": research_path,
        "article": article_path,
        "feedback": feedback_path,
        "workflow": workflow_path
    }

async def run_batch_research(topics: List[str], output_dir: str, verbose: bool = False) -> Dict[str, str]:
    """批量执行话题研究
    
    Args:
        topics: 话题列表
        output_dir: 输出目录
        verbose: 是否详细输出
        
    Returns:
        Dict[str, str]: 结果文件路径字典
    """
    logger.info(f"开始批量研究 {len(topics)} 个话题")
    
    results = {}
    for idx, topic in enumerate(topics):
        logger.info(f"处理第 {idx+1}/{len(topics)} 个话题: {topic}")
        result_path = await run_research(topic, output_dir, verbose)
        results[topic] = result_path
    
    # 保存批处理摘要
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_topics": len(topics),
        "topics": topics,
        "results": results
    }
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = save_results(summary, output_dir, f"batch_summary_{timestamp}.json")
    
    logger.info(f"批量研究完成，共 {len(topics)} 个话题")
    return results

async def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="研究团队运行脚本")
    parser.add_argument("--mode", "-m", type=str, required=True, 
                        choices=["research", "full", "batch"],
                        help="运行模式: research=仅研究, full=完整工作流, batch=批量研究")
    parser.add_argument("--topic", "-t", type=str, 
                        help="研究话题 (单个话题模式)")
    parser.add_argument("--topics-file", "-f", type=str,
                        help="话题列表文件 (批量模式)")
    parser.add_argument("--output-dir", "-o", type=str, default="./results",
                        help="输出目录")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="详细输出")
    
    args = parser.parse_args()
    
    # 确认输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 根据模式执行相应的操作
    if args.mode == "research":
        if not args.topic:
            parser.error("研究模式需要提供 --topic 参数")
        await run_research(args.topic, args.output_dir, args.verbose)
    
    elif args.mode == "full":
        if not args.topic:
            parser.error("完整工作流模式需要提供 --topic 参数")
        await run_full_workflow(args.topic, args.output_dir, args.verbose)
    
    elif args.mode == "batch":
        if not args.topics_file:
            parser.error("批量模式需要提供 --topics-file 参数")
        
        # 读取话题列表
        with open(args.topics_file, 'r', encoding='utf-8') as f:
            topics = [line.strip() for line in f if line.strip()]
        
        if not topics:
            logger.error("话题列表为空")
            sys.exit(1)
        
        logger.info(f"从文件 {args.topics_file} 中读取到 {len(topics)} 个话题")
        await run_batch_research(topics, args.output_dir, args.verbose)

if __name__ == "__main__":
    # 使用asyncio运行异步主函数
    import asyncio
    asyncio.run(main()) 