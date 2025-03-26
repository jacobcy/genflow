#!/usr/bin/env python
"""
写作团队运行脚本

提供命令行接口运行文章写作流程。

用法示例：
    python -m core.agents.writing_crew.run --title "Python异步编程最佳实践" --platform "掘金"
"""
import os
import sys
import json
import logging
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.models.article import Article, Section
from core.models.platform import Platform
from core.agents.writing_crew.writing_crew import WritingCrew, WritingResult
from core.agents.writing_crew.get_human_feedback import get_human_feedback

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("writing_crew.run")

# 平台预设
PLATFORM_PRESETS = {
    "zhihu": {
        "name": "知乎",
        "url": "https://www.zhihu.com",
        "content_rules": {
            "min_words": 800,
            "max_words": 10000,
            "allowed_tags": ["科技", "编程", "人工智能", "互联网"]
        }
    },
    "juejin": {
        "name": "掘金",
        "url": "https://juejin.cn",
        "content_rules": {
            "min_words": 1000,
            "max_words": 8000,
            "allowed_tags": ["前端", "后端", "Python", "JavaScript", "AI"]
        }
    },
    "wechat": {
        "name": "微信公众号",
        "url": "https://mp.weixin.qq.com",
        "content_rules": {
            "min_words": 1000,
            "max_words": 5000,
            "allowed_tags": ["科技", "商业", "生活", "文化"]
        }
    }
}

def get_platform(platform_name: str) -> Platform:
    """获取平台配置
    
    Args:
        platform_name: 平台名称
        
    Returns:
        Platform: 平台配置对象
    """
    platform_name = platform_name.lower()
    if platform_name in PLATFORM_PRESETS:
        preset = PLATFORM_PRESETS[platform_name]
        return Platform(
            id=f"platform_{platform_name}",
            name=preset["name"],
            url=preset["url"],
            content_rules=preset["content_rules"]
        )
    else:
        # 默认平台
        return Platform(
            id="platform_default",
            name=platform_name,
            url="",
            content_rules={
                "min_words": 800,
                "max_words": 5000,
                "allowed_tags": []
            }
        )

async def run_writing_workflow(args):
    """运行写作工作流
    
    Args:
        args: 命令行参数
    """
    try:
        # 获取平台
        platform = get_platform(args.platform)
        logger.info(f"使用平台: {platform.name}")
        
        # 创建文章
        article_id = f"article_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 创建初始章节
        sections = []
        if args.outline:
            # 从文件读取大纲
            try:
                with open(args.outline, 'r', encoding='utf-8') as f:
                    outline_data = json.load(f)
                    
                if isinstance(outline_data, list):
                    for i, item in enumerate(outline_data):
                        if isinstance(item, str):
                            sections.append(Section(
                                title=item,
                                content="",
                                order=i+1
                            ))
                        elif isinstance(item, dict) and "title" in item:
                            sections.append(Section(
                                title=item["title"],
                                content=item.get("content", ""),
                                order=i+1
                            ))
                elif isinstance(outline_data, dict) and "sections" in outline_data:
                    for i, item in enumerate(outline_data["sections"]):
                        if isinstance(item, dict) and "title" in item:
                            sections.append(Section(
                                title=item["title"],
                                content=item.get("content", ""),
                                order=i+1
                            ))
            except Exception as e:
                logger.warning(f"读取大纲文件失败: {e}，将使用空大纲")
        
        # 如果没有章节，创建一个默认章节
        if not sections:
            sections = [
                Section(
                    title="引言",
                    content="本文将探讨这个主题的各个方面。",
                    order=1
                )
            ]
        
        # 创建文章对象
        article = Article(
            id=article_id,
            topic_id=args.topic_id or f"topic_{article_id}",
            title=args.title,
            summary=args.summary or f"{args.title}的探讨与分析。",
            sections=sections,
            status="draft"
        )
        
        logger.info(f"创建文章: {article.title}, ID: {article.id}")
        
        # 创建写作团队
        crew = WritingCrew(verbose=args.verbose)
        
        # 执行写作流程
        logger.info("开始执行写作流程")
        writing_result = await crew.write_article(article, platform)
        
        # 保存原始结果
        output_path = args.output or "output"
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        result_file = output_dir / f"{article_id}_result.json"
        writing_result.save_to_file(str(result_file))
        logger.info(f"写作结果已保存到: {result_file}")
        
        # 是否需要人工反馈
        if not args.no_feedback:
            writing_result = get_human_feedback(writing_result)
            
            # 更新反馈结果
            feedback_file = output_dir / f"{article_id}_feedback.json"
            with open(feedback_file, "w", encoding="utf-8") as f:
                json.dump(writing_result.to_dict(), f, ensure_ascii=False, indent=2)
            logger.info(f"反馈结果已保存到: {feedback_file}")
            
            # 如果评分达标，更新文章
            threshold = args.threshold or 0.7
            if writing_result.human_feedback and writing_result.human_feedback.get("normalized_average_score", 0) >= threshold:
                logger.info(f"评分达标(>={threshold})，更新文章")
                article = crew.update_article(writing_result)
                
                # 保存最终文章
                final_file = output_dir / f"{article_id}_final.json"
                with open(final_file, "w", encoding="utf-8") as f:
                    # 将文章对象转换为字典
                    article_dict = {
                        "id": article.id,
                        "title": article.title,
                        "summary": article.summary,
                        "sections": [
                            {"title": s.title, "content": s.content, "order": s.order}
                            for s in article.sections
                        ],
                        "status": article.status,
                        "metadata": article.metadata
                    }
                    json.dump(article_dict, f, ensure_ascii=False, indent=2)
                logger.info(f"最终文章已保存到: {final_file}")
        
        logger.info("写作工作流完成")
        return 0
        
    except Exception as e:
        logger.error(f"写作工作流失败: {e}", exc_info=True)
        return 1

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="运行写作团队")
    
    # 必选参数
    parser.add_argument("--title", required=True, help="文章标题")
    
    # 可选参数
    parser.add_argument("--platform", default="zhihu", help="目标平台，如zhihu, juejin, wechat等")
    parser.add_argument("--summary", help="文章摘要")
    parser.add_argument("--topic-id", help="相关主题ID")
    parser.add_argument("--outline", help="大纲JSON文件路径")
    parser.add_argument("--output", help="输出目录")
    parser.add_argument("--threshold", type=float, help="评分通过阈值，默认0.7")
    parser.add_argument("--no-feedback", action="store_true", help="跳过人工反馈")
    parser.add_argument("--verbose", action="store_true", help="显示详细日志")
    
    args = parser.parse_args()
    
    # 运行写作工作流
    return asyncio.run(run_writing_workflow(args))

if __name__ == "__main__":
    sys.exit(main()) 