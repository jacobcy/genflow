"""内容采集示例"""
import asyncio
from src.config import Config
from src.collector.content import ContentCollector
from loguru import logger

async def main():
    """主函数"""
    # 初始化配置
    config = Config()
    
    # 初始化内容采集器
    collector = ContentCollector(config)
    
    # 搜索示例
    keyword = "人工智能最新发展"
    logger.info(f"搜索关键词: {keyword}")
    
    results = await collector.search_all(keyword)
    logger.info(f"找到 {len(results)} 条搜索结果")
    
    # 获取前3个结果的详细内容
    for i, result in enumerate(results[:3], 1):
        logger.info(f"\n--- 文章 {i} ---")
        logger.info(f"标题: {result['title']}")
        logger.info(f"URL: {result['url']}")
        
        content = await collector.get_content(result['url'])
        if content:
            logger.info(f"摘要: {content.summary}")
            logger.info(f"内容长度: {len(content.content)} 字符")
        else:
            logger.warning(f"无法获取内容")
            
    # 批量采集示例
    urls = [result['url'] for result in results[:5]]
    logger.info("\n=== 批量采集示例 ===")
    logger.info(f"准备采集 {len(urls)} 个URL")
    
    contents = await collector.batch_collect(urls)
    logger.info(f"成功采集 {len(contents)} 篇文章")
    
    # 网站爬取示例
    website_url = "https://www.example.com"
    logger.info("\n=== 网站爬取示例 ===")
    logger.info(f"准备爬取网站: {website_url}")
    
    pages = await collector.crawl_website(website_url, max_pages=5)
    logger.info(f"成功爬取 {len(pages)} 个页面")
    
if __name__ == "__main__":
    # 设置日志格式
    logger.add("logs/content_collection_{time}.log", rotation="500 MB")
    
    # 运行异步主函数
    asyncio.run(main()) 