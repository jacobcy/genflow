"""命令行入口"""
import asyncio
from core.controllers.content_controller import ContentController
from core.models.platform import PLATFORM_CONFIGS

async def main():
    """主程序入口"""
    # 先初始化controller为None，避免在异常处理中出现未定义错误
    controller = None
    try:
        # 创建内容控制器
        controller = ContentController()

        # 1. 选择目标平台
        print("\n=== 选择目标平台 ===\n")
        for idx, (platform_id, platform) in enumerate(PLATFORM_CONFIGS.items(), 1):
            print(f"{idx}. {platform.name}")

        while True:
            try:
                choice = int(input("\n请选择目标平台 (输入序号): "))
                if 1 <= choice <= len(PLATFORM_CONFIGS):
                    platform = list(PLATFORM_CONFIGS.values())[choice - 1]
                    break
                print("无效的选择，请重试")
            except ValueError:
                print("请输入有效的数字")

        # 2. 输入内容类别
        category = input("\n请输入内容类别 (如: 技术、生活、教育等): ").strip()
        topic_count = int(input("需要生成几篇文章? (1-5): ").strip())
        topic_count = max(1, min(5, topic_count))  # 限制范围

        # 3. 执行内容生产流程
        results = await controller.produce_content(
            category=category,
            platform=platform,
            topic_count=topic_count
        )

        # 4. 打印生产进度摘要
        progress = controller.get_progress()
        print("\n=== 生产进度摘要 ===")
        print(f"生产ID: {progress['production_id']}")
        print(f"总进度: {progress['progress_percentage']}%")
        print(f"总耗时: {progress['duration']:.2f}秒")
        print(f"完成文章数: {progress['completed_topics']}/{progress['total_topics']}")

        # 5. 打印生产结果
        if results:
            print("\n=== 生产结果 ===")
            for result in results:
                print(f"\n文章: {result.article.title}")
                print(f"平台: {result.platform.name}")
                print(f"状态: {result.status}")

                print("\n是否查看完整内容? (y/n)")
                if input().lower().strip() == 'y':
                    print("\n=== 完整内容 ===")
                    print(f"标题: {result.article.title}")
                    print(f"摘要: {result.article.summary}")
                    print("\n正文:")
                    for section in result.article.sections:
                        print(f"\n{section.title}")
                        print(section.content)
        else:
            print("\n未能生成符合要求的文章")

    except KeyboardInterrupt:
        print("\n已取消生产")
        if controller:
            controller.pause_production()
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        # 打印错误日志
        if controller and hasattr(controller, 'current_progress'):
            print("\n错误日志:")
            for error in controller.current_progress.error_logs:
                print(f"- [{error['stage']}] {error['time']}: {error['error']}")

if __name__ == "__main__":
    asyncio.run(main())
