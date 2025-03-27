import asyncio
from core.models.platform import Platform
from core.models.article_style import ContentRules, StyleRules, StyleGuide
from core.controllers.content_controller import ContentController


# 使用示例
async def main():
    """主函数"""
    try:
        # 创建一个示例平台
        platform = Platform(
            id="zhihu",
            name="知乎",
            type="knowledge_sharing",
            url="https://www.zhihu.com",
            description="知名问答社区与专业内容平台",
            target_audience="20-40岁高学历人群",
            content_types=["popular_science", "professional_analysis"],
            primary_language="zh-CN",
            content_rules=ContentRules(
                min_length=1000,
                max_length=20000,
                allowed_formats=["text", "image", "code"],
                forbidden_words=["广告", "推广"],
                required_sections=["引言", "正文", "总结"]
            ),
            style_rules=StyleRules(
                tone="professional",
                formality=4,
                emotion=False,
                code_block=True,
                emoji=False,
                image_text_ratio=0.2,
                max_image_count=10,
                min_paragraph_length=100,
                max_paragraph_length=500
            ),
            style_guide=StyleGuide(
                tone="professional",
                format="article",
                target_audience="professionals",
                writing_style="analytical",
                language_level="advanced",
                content_approach="informative"
            ),
            publish_settings={
                "auto_publish": False,
                "review_required": True
            }
        )

        # 创建控制器
        controller = ContentController()

        # 生产内容
        results = await controller.produce_content(
            category="技术",
            content_type="professional_analysis",
            platform=platform,
            style="professional",
            options={
                "topic_count": 1,
                "mode": "auto"
            }
        )

        # 打印进度摘要
        progress = controller.get_progress()
        print("\n=== 生产进度摘要 ===")
        print(f"生产ID: {progress['production_id']}")
        print(f"当前阶段: {progress['current_stage']}")
        print(f"阶段状态: {progress['stage_status']}")
        print(f"总进度: {progress['progress_percentage']}%")
        print(f"总耗时: {progress['duration']:.2f}秒")

        # 打印生产结果
        print("\n=== 生产结果 ===")
        if "final_article" in results:
            print(f"文章: {results['final_article']['title']}")
        elif "final_articles" in results:
            for idx, article in enumerate(results["final_articles"]):
                print(f"\n文章 {idx+1}: {article['title']}")

        print(f"状态: {results['status']}")
        print(f"耗时: {results['duration_seconds']:.2f}秒")

    except Exception as e:
        print(f"\n生产失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
