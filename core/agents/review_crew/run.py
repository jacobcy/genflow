#!/usr/bin/env python
"""
审核团队运行脚本

提供命令行接口运行文章审核流程。

用法示例：
    python -m core.agents.review_crew.run --article-id "article_202405010001" --platform "掘金"
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
from core.agents.review_crew.review_crew import ReviewCrew, ReviewResult
from core.agents.review_crew.get_human_feedback import get_human_feedback

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("review_crew.run")

# 平台预设
PLATFORM_PRESETS = {
    "zhihu": {
        "name": "知乎",
        "url": "https://www.zhihu.com",
        "content_rules": {
            "min_words": 800,
            "max_words": 10000,
            "allowed_tags": ["科技", "编程", "人工智能", "互联网"],
            "sensitive_words": ["敏感词1", "敏感词2"]
        }
    },
    "juejin": {
        "name": "掘金",
        "url": "https://juejin.cn",
        "content_rules": {
            "min_words": 1000,
            "max_words": 8000,
            "allowed_tags": ["前端", "后端", "Python", "JavaScript", "AI"],
            "sensitive_words": ["敏感词1", "敏感词2"]
        }
    },
    "wechat": {
        "name": "微信公众号",
        "url": "https://mp.weixin.qq.com",
        "content_rules": {
            "min_words": 1000,
            "max_words": 5000,
            "allowed_tags": ["科技", "商业", "生活", "文化"],
            "sensitive_words": ["敏感词1", "敏感词2", "敏感词3"]
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
                "allowed_tags": [],
                "sensitive_words": []
            }
        )

def load_article(article_file: str) -> Article:
    """从文件加载文章
    
    Args:
        article_file: 文章JSON文件路径
        
    Returns:
        Article: 文章对象
    """
    try:
        with open(article_file, 'r', encoding='utf-8') as f:
            article_data = json.load(f)
        
        # 转换section格式
        sections = []
        if "sections" in article_data:
            for i, section_data in enumerate(article_data["sections"]):
                if isinstance(section_data, dict):
                    sections.append(Section(
                        title=section_data.get("title", f"第{i+1}节"),
                        content=section_data.get("content", ""),
                        order=section_data.get("order", i+1)
                    ))
                elif isinstance(section_data, str):
                    sections.append(Section(
                        title=f"第{i+1}节",
                        content=section_data,
                        order=i+1
                    ))
        
        # 创建文章对象
        return Article(
            id=article_data.get("id", f"article_{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            topic_id=article_data.get("topic_id", ""),
            title=article_data.get("title", "无标题文章"),
            summary=article_data.get("summary", ""),
            sections=sections,
            status=article_data.get("status", "pending_review"),
            metadata=article_data.get("metadata", {})
        )
    except Exception as e:
        logger.error(f"加载文章文件失败: {e}")
        raise ValueError(f"无法解析文章文件: {e}")

async def run_review_workflow(args):
    """运行审核工作流
    
    Args:
        args: 命令行参数
    """
    try:
        # 获取平台
        platform = get_platform(args.platform)
        logger.info(f"使用平台: {platform.name}")
        
        # 获取文章
        if args.article_file:
            # 从文件加载文章
            article = load_article(args.article_file)
            logger.info(f"从文件加载文章: {article.title}")
        elif args.article_id:
            # 尝试从数据库或文件系统加载文章
            # 这里简化处理，创建一个示例文章
            article = Article(
                id=args.article_id,
                topic_id=args.topic_id or f"topic_{args.article_id}",
                title=args.title or "待审核文章",
                summary=args.summary or "文章摘要",
                sections=[
                    Section(
                        title="文章正文",
                        content=args.content or "这是文章的正文内容。",
                        order=1
                    )
                ],
                status="pending_review"
            )
            logger.info(f"创建示例文章: {article.title}, ID: {article.id}")
        else:
            raise ValueError("必须提供article_id或article_file参数")
        
        # 创建审核团队
        crew = ReviewCrew(verbose=args.verbose)
        
        # 执行审核流程
        logger.info("开始执行审核流程")
        review_result = await crew.review_article(article, platform)
        
        # 保存原始结果
        output_path = args.output or "output"
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        result_file = output_dir / f"review_{article.id}_result.json"
        review_result.save_to_file(str(result_file))
        logger.info(f"审核结果已保存到: {result_file}")
        
        # 是否需要人工反馈
        if not args.no_feedback:
            review_result = get_human_feedback(review_result)
            
            # 更新反馈结果
            feedback_file = output_dir / f"review_{article.id}_feedback.json"
            with open(feedback_file, "w", encoding="utf-8") as f:
                json.dump(review_result.to_dict(), f, ensure_ascii=False, indent=2)
            logger.info(f"反馈结果已保存到: {feedback_file}")
            
            # 如果评分达标，更新文章状态
            threshold = args.threshold or 0.7
            if review_result.human_feedback and review_result.human_feedback.get("normalized_average_score", 0) >= threshold:
                logger.info(f"评分达标(>={threshold})，更新文章状态")
                article = crew.update_article_status(review_result)
                
                # 保存最终文章
                final_file = output_dir / f"article_{article.id}_reviewed.json"
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
                        "metadata": article.metadata,
                        "review_data": article.review_data
                    }
                    json.dump(article_dict, f, ensure_ascii=False, indent=2)
                logger.info(f"审核后的文章已保存到: {final_file}")
                
                # 打印审核结果摘要
                print("\n" + "="*50)
                print(" 审核结果摘要 ".center(50, "="))
                print("="*50)
                print(f"\n文章: {article.title}")
                print(f"状态: {article.status}")
                print(f"查重率: {article.review_data.get('plagiarism_rate', 'N/A')}")
                print(f"AI分数: {article.review_data.get('ai_score', 'N/A')}")
                print(f"风险等级: {article.review_data.get('risk_level', 'N/A')}")
                
                # 打印改进建议
                if article.review_data.get("review_comments"):
                    print("\n改进建议:")
                    for i, suggestion in enumerate(article.review_data.get("review_comments", []), 1):
                        if isinstance(suggestion, dict) and "suggestion" in suggestion:
                            print(f"{i}. {suggestion.get('aspect', '')}: {suggestion.get('suggestion', '')}")
                        else:
                            print(f"{i}. {suggestion}")
        
        logger.info("审核工作流完成")
        return 0
        
    except Exception as e:
        logger.error(f"审核工作流失败: {e}", exc_info=True)
        return 1

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="运行审核团队")
    
    # 文章来源参数（二选一）
    article_group = parser.add_mutually_exclusive_group(required=True)
    article_group.add_argument("--article-id", help="要审核的文章ID")
    article_group.add_argument("--article-file", help="要审核的文章JSON文件路径")
    
    # 文章内容参数（与article-id一起使用）
    parser.add_argument("--title", help="文章标题，仅在使用--article-id时有效")
    parser.add_argument("--summary", help="文章摘要，仅在使用--article-id时有效")
    parser.add_argument("--content", help="文章内容，仅在使用--article-id时有效")
    parser.add_argument("--topic-id", help="相关主题ID，仅在使用--article-id时有效")
    
    # 审核选项
    parser.add_argument("--platform", default="zhihu", help="目标平台，如zhihu, juejin, wechat等")
    parser.add_argument("--output", help="输出目录")
    parser.add_argument("--threshold", type=float, help="评分通过阈值，默认0.7")
    parser.add_argument("--no-feedback", action="store_true", help="跳过人工反馈")
    parser.add_argument("--verbose", action="store_true", help="显示详细日志")
    
    args = parser.parse_args()
    
    # 运行审核工作流
    return asyncio.run(run_review_workflow(args))

if __name__ == "__main__":
    sys.exit(main()) 