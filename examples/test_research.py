import asyncio
import logging
from core.agents.research_crew import ResearchCrew

# 配置日志
logging.basicConfig(level=logging.INFO)

async def test():
    """测试研究团队执行特定内容类型的研究任务"""
    print("初始化研究团队...")
    crew = ResearchCrew()

    print("开始研究任务...")
    result = await crew.research_topic('人工智能发展历史', content_type='博客')

    print(f"研究结果类型: {type(result).__name__}")
    print(f"研究主题: {result.topic}")
    print(f"研究配置: {result.metadata.get('research_config', {})}")

    return result

if __name__ == "__main__":
    asyncio.run(test())
