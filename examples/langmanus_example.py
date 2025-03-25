"""
展示如何在 GenFlow 中使用 LangManus 的能力
"""
import asyncio
from core.integrations.langmanus import LangManusClient

async def main():
    # 初始化客户端
    client = LangManusClient()
    
    try:
        # 示例 1: 研究主题
        topic = "AI 写作的最新趋势"
        research_result = await client.research(topic)
        print("研究结果:", research_result)
        
        # 示例 2: 分析文章
        article = """
        人工智能正在改变写作方式。
        它不仅能够辅助写作，还能提供灵感和建议。
        但是，人类的创造力仍然是不可替代的。
        """
        analysis_result = await client.analyze(article)
        print("分析结果:", analysis_result)
        
    finally:
        # 确保关闭客户端
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())