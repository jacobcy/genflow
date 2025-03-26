#!/usr/bin/env python3
"""测试风格团队与风格类型模块的集成

这个脚本测试style_crew模块是否能正确使用style_types模块获取平台风格信息。
"""

import logging
import asyncio
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple

# 首先定义测试用的Platform和StyleRules类
@dataclass
class StyleRules:
    tone: str
    formality: int
    emotion: bool
    code_block: bool
    emoji: bool
    image_text_ratio: float
    max_image_count: int
    min_paragraph_length: int
    max_paragraph_length: int
    paragraph_count_range: Tuple[int, int]
    section_count_range: Tuple[int, int]
    title_length_range: Tuple[int, int]
    keyword_density: float
    heading_required: bool
    tag_count_range: Tuple[int, int]

@dataclass
class Platform:
    id: str
    name: str
    type: str
    url: str
    description: str = ""
    target_audience: str = ""
    content_types: List[str] = field(default_factory=list)
    style_rules: Optional[StyleRules] = None

    def to_dict(self):
        result = asdict(self)
        if self.style_rules:
            result["style_rules"] = asdict(self.style_rules)
        return result

# 现在导入风格团队和风格类型模块
from core.agents.style_crew import StyleCrew
from core.constants.style_types import (
    ALL_STYLE_TYPES,
    PLATFORM_TO_STYLE_MAP,
    get_platform_style_type,
    get_style_features,
    get_style_description
)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def create_default_style_rules() -> StyleRules:
    """\u521b\u5efa\u4e00\u4e2a\u9ed8\u8ba4\u7684\u98ce\u683c\u89c4\u5219"""
    return StyleRules(
        tone="neutral",
        formality=3,
        emotion=False,
        code_block=True,
        emoji=False,
        image_text_ratio=0.2,
        max_image_count=20,
        min_paragraph_length=30,
        max_paragraph_length=300,
        paragraph_count_range=(5, 20),
        section_count_range=(3, 10),
        title_length_range=(20, 100),
        keyword_density=0.02,
        heading_required=True,
        tag_count_range=(3, 10)
    )

async def test_style_integration():
    """测试风格团队与风格类型模块的集成"""
    logger.info("开始测试风格团队与风格类型模块的集成...")

    # 遍历部分已定义的平台映射
    test_platforms = ["zhihu", "xiaohongshu", "weibo", "bilibili"]

    for platform_id in test_platforms:
        style_type = get_platform_style_type(platform_id)
        if not style_type:
            logger.warning(f"\u5e73\u53f0 {platform_id} \u6ca1\u6709\u5bf9\u5e94\u7684\u98ce\u683c\u7c7b\u578b\uff0c\u8df3\u8fc7")
            continue

        logger.info(f"\n测试平台 '{platform_id}' -> 风格 '{style_type}'")

        # 创建平台对象
        platform = Platform(
            id=platform_id,
            name=style_type,
            type="demo",
            url=f"https://www.{platform_id}.com",
            description=f"{style_type}风格的内容平台",
            target_audience="广大用户",
            content_types=["article", "post"],
            style_rules=create_default_style_rules()
        )

        # 获取风格特征
        style_features = get_style_features(style_type)
        style_description = get_style_description(style_type)
        logger.info(f"  风格描述: {style_description}")
        logger.info(f"  语调: {style_features.get('tone')}")
        logger.info(f"  正式程度: {style_features.get('formality')}")

        # 创建风格团队
        try:
            style_crew = StyleCrew()
            style_crew.initialize(platform)
            logger.info(f"  风格团队已初始化，使用平台: {platform.id}")
        except Exception as e:
            logger.error(f"  初始化风格团队失败: {str(e)}")

    logger.info("\n风格团队与风格类型模块集成测试完成")

async def main():
    """主函数"""
    await test_style_integration()

if __name__ == "__main__":
    asyncio.run(main())
