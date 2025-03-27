"""内容类型配置管理

该模块处理内容类型配置的迁移。用于旧配置格式与新配置格式的兼容处理。
"""

import os
import json
import shutil
from typing import Dict, Any, List
from pathlib import Path
from loguru import logger

def migrate_legacy_config():
    """迁移旧版本的内容类型配置

    将单一的 content_types.json 文件拆分为多个独立的配置文件
    """
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.dirname(current_dir)

    # 旧配置文件路径
    legacy_file = os.path.join(models_dir, 'content_types.json')
    if not os.path.exists(legacy_file):
        logger.info("没有找到旧版配置文件，无需迁移")
        return

    # 确保配置目录存在
    config_dir = current_dir
    os.makedirs(config_dir, exist_ok=True)

    try:
        # 读取旧配置
        with open(legacy_file, 'r', encoding='utf-8') as f:
            legacy_config = json.load(f)

        # 检查是否已经迁移过
        if os.path.exists(os.path.join(config_dir, 'category_mapping.json')):
            file_count = len([f for f in os.listdir(config_dir) if f.endswith('.json')])
            if file_count > 5:  # 已经有足够多的配置文件，可能已经迁移过
                logger.info("配置目录中已有多个配置文件，可能已经迁移过")
                return

        # 备份旧配置
        backup_file = legacy_file + '.bak'
        shutil.copy2(legacy_file, backup_file)
        logger.info(f"已备份旧配置到 {backup_file}")

        # 提取并保存常量配置
        constants = legacy_config.get('constants', {})
        if constants:
            with open(os.path.join(config_dir, 'category_mapping.json'), 'w', encoding='utf-8') as f:
                json.dump(constants, f, ensure_ascii=False, indent=4)
            logger.info("已保存类别映射配置")

        # 内容类型 ID 映射
        content_type_ids = {
            "快讯": "news_flash",
            "社交媒体": "social_media",
            "新闻": "news",
            "博客": "blog",
            "教程": "tutorial",
            "评测": "review",
            "故事": "story",
            "技术": "technical",
            "问答": "qa",
            "娱乐": "entertainment",
            "生活": "lifestyle",
            "科普": "popular_science",
            "论文": "academic_paper",
            "研究报告": "report",
            "分析": "analysis"
        }

        # 内容类型分类映射
        category_mapping = {
            "news_flash": "NEWS",
            "social_media": "OTHER",
            "news": "NEWS",
            "blog": "BLOG",
            "tutorial": "TUTORIAL",
            "review": "REVIEW",
            "story": "STORY",
            "technical": "OTHER",
            "qa": "OTHER",
            "entertainment": "OTHER",
            "lifestyle": "OTHER",
            "popular_science": "OTHER",
            "academic_paper": "OTHER",
            "report": "REPORT",
            "analysis": "OTHER"
        }

        # 遍历所有内容类型，创建独立配置文件
        research_config = legacy_config.get('research_config', {})
        writing_config = legacy_config.get('writing_config', {})

        for zh_name, content_type_id in content_type_ids.items():
            if zh_name in research_config and zh_name in writing_config:
                content_config = create_content_type_config(
                    content_type_id,
                    zh_name,
                    category_mapping.get(content_type_id, "OTHER"),
                    research_config[zh_name],
                    writing_config[zh_name]
                )

                # 保存配置
                config_file = os.path.join(config_dir, f"{content_type_id}.json")
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(content_config, f, ensure_ascii=False, indent=4)

                logger.info(f"已保存 {zh_name} 配置到 {content_type_id}.json")

        logger.info("配置迁移完成")

    except Exception as e:
        logger.error(f"配置迁移失败: {str(e)}")

def create_content_type_config(content_id: str, name: str, category: str,
                              research_config: Dict[str, Any],
                              writing_config: Dict[str, Any]) -> Dict[str, Any]:
    """根据旧配置创建新的内容类型配置

    Args:
        content_id: 内容类型ID
        name: 内容类型名称
        category: 内容类型分类
        research_config: 研究配置
        writing_config: 写作配置

    Returns:
        Dict[str, Any]: 新的内容类型配置
    """
    # 解析写作配置中的字数范围
    word_count = writing_config.get('word_count', '1000-3000')
    if isinstance(word_count, str) and '-' in word_count:
        min_length, max_length = map(int, word_count.split('-'))
    else:
        min_length, max_length = 1000, 3000

    # 确定是否需要代码
    is_technical = name in ["技术", "教程", "问答"]

    # 确定是否需要图片
    requires_images = name in ["评测", "社交媒体", "新闻", "科普"]

    # 解析写作风格
    style = writing_config.get('style', '')
    is_creative = "生动" in style or "对话" in style or "叙事" in style
    is_formal = "严谨" in style or "客观" in style or "分析" in style

    # 根据深度设置研究强度
    depth = research_config.get('depth', '中等')
    research_intensity = 3  # 默认中等
    if depth == "轻量":
        research_intensity = 1
    elif depth == "深度":
        research_intensity = 5

    # 设置主要目的
    primary_purpose = "inform"
    if name in ["教程", "问答", "科普"]:
        primary_purpose = "educate"
    elif name in ["评测"]:
        primary_purpose = "evaluate"
    elif name in ["故事", "娱乐"]:
        primary_purpose = "entertain"
    elif name in ["分析", "研究报告"]:
        primary_purpose = "analyze"

    # 设置格式
    format_type = "standard"
    if name in ["快讯", "社交媒体"]:
        format_type = "short-form"
    elif name in ["论文", "研究报告", "分析"]:
        format_type = "long-form"
    elif name in ["教程"]:
        format_type = "instructional"
    elif name in ["故事"]:
        format_type = "narrative"

    # 创建兼容的风格列表
    compatible_styles = []
    if is_formal:
        compatible_styles.extend(["formal", "professional"])
    else:
        compatible_styles.extend(["casual", "conversational"])

    if is_creative:
        compatible_styles.extend(["creative", "engaging"])
    else:
        compatible_styles.extend(["informative", "analytical"])

    # 创建结构模板
    structure = writing_config.get('structure', '引言-主体-结论')
    sections = [s.strip() for s in structure.split('-')]

    structure_template = {
        "name": f"{name}模板",
        "description": f"标准{name}结构",
        "sections": sections,
        "outline_template": {
            f"section_{i+1}": sections[i] for i in range(len(sections))
        },
        "examples": [f"{name}示例"]
    }

    # 创建内容类型配置
    config = {
        "id": content_id,
        "name": name,
        "category": category,
        "description": f"{research_config.get('description', '')}",
        "format": format_type,
        "primary_purpose": primary_purpose,
        "structure_templates": [structure_template],
        "format_guidelines": {
            "min_length": min_length,
            "max_length": max_length,
            "min_section_count": len(sections),
            "max_section_count": len(sections) * 2,
            "recommended_section_length": max_length // (len(sections) or 1),
            "title_guidelines": {
                "min_length": 5,
                "max_length": 100,
                "format": "descriptive"
            },
            "requires_images": requires_images,
            "requires_code": is_technical
        },
        "characteristics": {
            "is_technical": is_technical,
            "is_creative": is_creative,
            "is_formal": is_formal,
            "is_timely": name in ["快讯", "新闻", "社交媒体"],
            "is_narrative": name in ["故事", "博客"],
            "is_instructional": name in ["教程", "问答"],
            "audience_level": "expert" if name in ["论文", "技术"] else "general",
            "multimedia_focus": requires_images,
            "research_intensity": research_intensity
        },
        "compatible_styles": compatible_styles,
        "example_topics": ["示例主题1", "示例主题2"],
        "metadata": {
            "version": 1,
            "last_updated": "2023-01-01",
            "source": "migrated"
        }
    }

    return config

if __name__ == "__main__":
    # 直接运行此模块时，执行迁移
    migrate_legacy_config()
