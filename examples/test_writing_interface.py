import asyncio
import sys
from pathlib import Path
from typing import Dict

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from core.services.writing.interface import WritingInterface


def print_dict(data: Dict, indent: int = 0):
    """格式化打印字典数据"""
    for key, value in data.items():
        if isinstance(value, dict):
            print("  " * indent + f"{key}:")
            print_dict(value, indent + 1)
        else:
            print("  " * indent + f"{key}: {value}")


async def main():
    """测试写作助手接口"""
    try:
        # 初始化写作接口
        interface = WritingInterface()

        # 设置文章信息
        title = "Python异步编程最佳实践"
        summary = "本文将介绍Python异步编程的核心概念和最佳实践，帮助读者掌握异步编程技巧。"

        # 设置平台规则
        content_rules = {
            "min_words": 2000,
            "max_words": 5000,
            "allowed_tags": ["python", "async", "programming"]
        }

        print("\n1. 开始生成文章...")
        result = await interface.write_article(
            title=title,
            summary=summary,
            platform_name="tech_blog",
            content_rules=content_rules
        )

        print("\n2. 写作结果:")
        print_dict(result)

        print("\n3. 获取写作反馈...")
        feedback = await interface.get_feedback(result)

        print("\n4. 反馈结果:")
        print_dict(feedback)

    except Exception as e:
        print(f"\n错误: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
