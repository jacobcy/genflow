"""命令行入口"""
import asyncio
import argparse
import random
from typing import List, Optional, Tuple
from core.controllers.content_controller import ContentController
from core.models.platform.platform import get_default_platform
from core.models.progress import ProductionStage

# 预定义类别和风格列表
CATEGORIES = [
    "科技", "财经", "教育", "健康", "娱乐", "体育", "生活",
    "文化", "社会", "政治", "环境", "旅游", "职场", "美食"
]

STYLES = [
    "专业严谨", "通俗易懂", "深度分析", "生动活泼",
    "故事化叙述", "观点鲜明", "简洁明了", "详尽全面"
]

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="GenFlow 内容生产系统")

    parser.add_argument("--category", type=str,
                        help=f"内容类别（可选：{', '.join(CATEGORIES)}，或random随机选择）")
    parser.add_argument("--style", type=str,
                        help=f"写作风格（可选：{', '.join(STYLES)}，或random随机选择）")
    parser.add_argument("--count", type=int, default=1, help="文章数量 (1-5)")
    parser.add_argument("--mode", type=str, choices=["auto", "human", "mixed"],
                        default="human", help="生产模式：auto(全自动), human(人工辅助), mixed(混合)")
    parser.add_argument("--auto-stages", type=str,
                        help="自动执行的阶段，逗号分隔，例如：topic_discovery,article_writing")

    return parser.parse_args()

def get_random_category() -> str:
    """随机选择一个类别"""
    return random.choice(CATEGORIES)

def get_random_style() -> str:
    """随机选择一个风格"""
    return random.choice(STYLES)

def parse_auto_stages(stages_str: str) -> List[str]:
    """解析自动执行阶段参数"""
    if not stages_str:
        return []
    return [stage.strip() for stage in stages_str.split(",") if stage.strip()]

async def interactive_mode() -> Tuple[str, str, int, str, Optional[List[str]]]:
    """交互式模式"""
    try:
        # 1. 选择内容类别
        print("\n=== 选择内容类别 ===\n")
        print("0. 随机选择")
        for idx, category in enumerate(CATEGORIES, 1):
            print(f"{idx}. {category}")

        while True:
            try:
                choice = int(input("\n请选择内容类别 (输入序号，0为随机): "))
                if choice == 0:
                    category = get_random_category()
                    print(f"已随机选择类别: {category}")
                    break
                elif 1 <= choice <= len(CATEGORIES):
                    category = CATEGORIES[choice - 1]
                    break
                print("无效的选择，请重试")
            except ValueError:
                print("请输入有效的数字")

        # 2. 选择写作风格
        print("\n=== 选择写作风格 ===\n")
        print("0. 随机选择")
        for idx, style in enumerate(STYLES, 1):
            print(f"{idx}. {style}")

        while True:
            try:
                choice = int(input("\n请选择写作风格 (输入序号，0为随机): "))
                if choice == 0:
                    style = get_random_style()
                    print(f"已随机选择风格: {style}")
                    break
                elif 1 <= choice <= len(STYLES):
                    style = STYLES[choice - 1]
                    break
                print("无效的选择，请重试")
            except ValueError:
                print("请输入有效的数字")

        # 3. 文章数量
        topic_count = int(input("\n需要生成几篇文章? (1-5): ").strip())
        topic_count = max(1, min(5, topic_count))  # 限制范围

        # 4. 选择生产模式
        print("\n=== 选择生产模式 ===\n")
        print("1. 全自动模式 - AI自动完成所有阶段")
        print("2. 全人工辅助模式 - 所有阶段都需要人工确认")
        print("3. 混合模式 - 自定义哪些阶段自动执行")

        while True:
            try:
                mode_choice = int(input("\n请选择模式 (输入序号): "))
                if 1 <= mode_choice <= 3:
                    if mode_choice == 1:
                        mode = 'auto'
                        auto_stages = None
                    elif mode_choice == 2:
                        mode = 'human'
                        auto_stages = None
                    else:
                        mode = 'mixed'
                        # 显示各专业团队说明
                        print("\n=== 专业团队介绍 ===")
                        stages = {
                            1: {
                                "name": "选题发现",
                                "value": "topic_discovery",
                                "description": "输入：类别（默认热门）\n输出：热词（可能有URL）\n功能：发现和推荐当前热门话题"
                            },
                            2: {
                                "name": "话题研究",
                                "value": "topic_research",
                                "description": "输入：热词（可能有URL）\n输出：热词+背景资料\n功能：收集话题相关的背景信息"
                            },
                            3: {
                                "name": "文章写作",
                                "value": "article_writing",
                                "description": "输入：热词+背景摘要\n输出：文章（标题、内容、关键词、摘要）\n功能：基于研究资料生成完整文章"
                            },
                            4: {
                                "name": "风格适配",
                                "value": "style_adaptation",
                                "description": "输入：风格、文章\n输出：风格化后的文章\n功能：根据指定风格调整文章表达方式"
                            },
                            5: {
                                "name": "文章审核",
                                "value": "article_review",
                                "description": "输入：文章\n输出：审核后的文章\n功能：进行查重和AI检测，确保文章质量"
                            }
                        }

                        # 选择自动执行的阶段
                        auto_stages = []
                        print("\n请选择需要自动执行的阶段 (其他阶段将需要人工辅助):")

                        for idx, info in stages.items():
                            print(f"\n{idx}. {info['name']}")
                            print(f"   {info['description']}")
                            choice = input(f"是否自动执行 {info['name']} 阶段? (y/n): ").strip().lower()
                            if choice == 'y' or choice == 'yes':
                                auto_stages.append(info["value"])
                    break
                print("无效的选择，请重试")
            except ValueError:
                print("请输入有效的数字")

        # 5. 显示配置摘要
        print("\n=== 生产配置摘要 ===")
        print(f"内容类别: {category}")
        print(f"写作风格: {style}")
        print(f"文章数量: {topic_count}")
        print(f"生产模式: {'全自动' if mode == 'auto' else '全人工辅助' if mode == 'human' else '混合'}")

        if mode == 'mixed':
            print("自动执行阶段:")
            for stage in auto_stages:
                for idx, info in stages.items():
                    if info["value"] == stage:
                        print(f"- {info['name']}")

        confirm = input("\n确认开始生产? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            print("已取消生产")
            return None, None, None, None, None

        return category, style, topic_count, mode, auto_stages

    except KeyboardInterrupt:
        print("\n已取消操作")
        return None, None, None, None, None
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        return None, None, None, None, None

async def main():
    """主程序入口"""
    # 解析命令行参数
    args = parse_arguments()

    # 处理类别参数
    if args.category is None or args.category.lower() == "random":
        category = get_random_category()
        print(f"已随机选择类别: {category}")
    else:
        if args.category in CATEGORIES:
            category = args.category
        else:
            print(f"警告: 未知类别 '{args.category}'，将随机选择")
            category = get_random_category()
            print(f"已随机选择类别: {category}")

    # 处理风格参数
    if args.style is None or args.style.lower() == "random":
        style = get_random_style()
        print(f"已随机选择风格: {style}")
    else:
        if args.style in STYLES:
            style = args.style
        else:
            print(f"警告: 未知风格 '{args.style}'，将随机选择")
            style = get_random_style()
            print(f"已随机选择风格: {style}")

    # 检查是否需要交互式模式 - 如果用户没有提供任何必需参数
    if not (hasattr(args, 'category') and hasattr(args, 'style')):
        category, style, topic_count, mode, auto_stages = await interactive_mode()
        if category is None:  # 如果交互式模式取消或出错
            return
    else:
        # 使用命令行参数
        topic_count = max(1, min(5, args.count))  # 限制范围
        mode = args.mode
        auto_stages = parse_auto_stages(args.auto_stages) if args.auto_stages else None

    # 显示配置摘要
    print("\n=== 生产配置摘要 ===")
    print(f"内容类别: {category}")
    print(f"写作风格: {style}")
    print(f"文章数量: {topic_count}")
    print(f"生产模式: {'全自动' if mode == 'auto' else '全人工辅助' if mode == 'human' else '混合'}")

    if mode == 'mixed' and auto_stages:
        stage_names = {
            "topic_discovery": "选题发现",
            "topic_research": "话题研究",
            "article_writing": "文章写作",
            "style_adaptation": "风格适配",
            "article_review": "文章审核"
        }
        print("自动执行阶段:")
        for stage in auto_stages:
            if stage in stage_names:
                print(f"- {stage_names[stage]}")

    # 创建控制器并执行内容生产
    controller = None
    try:
        # 创建内容控制器
        controller = ContentController()

        # 获取默认平台
        platform = get_default_platform()

        # 执行内容生产流程
        results = await controller.produce_content(
            category=category,
            platform=platform,
            topic_count=topic_count,
            mode=mode,
            auto_stages=auto_stages,
            style=style
        )

        # 打印生产进度摘要
        progress = controller.get_progress()
        print("\n=== 生产进度摘要 ===")
        print(f"生产ID: {progress['production_id']}")
        print(f"生产模式: {'全自动' if mode == 'auto' else '全人工辅助' if mode == 'human' else '混合'}")
        print(f"总进度: {progress['progress_percentage']}%")
        print(f"总耗时: {progress['duration']:.2f}秒")
        print(f"完成文章数: {progress['completed_topics']}/{progress['total_topics']}")

        # 打印生产结果
        if results:
            print("\n=== 生产结果 ===")
            for result in results:
                print(f"\n文章: {result.article.title}")
                print(f"风格: {style}")
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
