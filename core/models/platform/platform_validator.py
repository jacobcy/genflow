"""平台验证工具

用于验证文章是否符合平台的要求和限制。
"""

from typing import Dict, List, Any, Optional
from loguru import logger

def validate_article_against_platform(article: Any, platform: Any) -> Dict[str, Any]:
    """验证文章是否符合平台要求

    Args:
        article: 文章对象，必须具有 title, content 属性
        platform: 平台对象，必须具有验证所需的约束属性

    Returns:
        Dict[str, Any]: 验证结果，包含是否通过验证和详细信息
        {
            "valid": bool,
            "message": str,
            "details": List[Dict[str, Any]]
        }
    """
    # 初始化结果
    result = {
        "valid": True,
        "message": "文章符合平台要求",
        "details": []
    }

    details = []

    # 验证标题长度
    if hasattr(article, 'title') and hasattr(platform, 'max_title_length'):
        title_length = len(article.title) if article.title else 0
        if title_length > platform.max_title_length:
            details.append({
                "type": "title_length",
                "valid": False,
                "message": f"标题长度超过限制 ({title_length}/{platform.max_title_length})"
            })

    # 验证内容长度
    if hasattr(article, 'content') and hasattr(platform, 'min_length') and hasattr(platform, 'max_length'):
        content_length = len(article.content) if article.content else 0

        # 检查最小长度
        if content_length < platform.min_length:
            details.append({
                "type": "min_length",
                "valid": False,
                "message": f"内容长度不足 ({content_length}/{platform.min_length})"
            })

        # 检查最大长度
        if content_length > platform.max_length:
            details.append({
                "type": "max_length",
                "valid": False,
                "message": f"内容长度超过限制 ({content_length}/{platform.max_length})"
            })

    # 检查禁用词
    if hasattr(article, 'content') and hasattr(platform, 'forbidden_words') and platform.forbidden_words:
        text = article.title + " " + article.content if article.title else article.content
        found_words = []

        # 检查每个禁用词
        for word in platform.forbidden_words:
            if word.lower() in text.lower():
                found_words.append(word)

        if found_words:
            details.append({
                "type": "forbidden_words",
                "valid": False,
                "message": f"内容包含禁用词: {', '.join(found_words)}",
                "words": found_words
            })

    # 计算图片数量（如果有相关属性）
    image_count = 0
    if hasattr(article, 'images'):
        image_count = len(article.images) if article.images else 0

    # 验证图片数量
    if hasattr(platform, 'max_image_count') and image_count > platform.max_image_count:
        details.append({
            "type": "max_image_count",
            "valid": False,
            "message": f"图片数量超过限制 ({image_count}/{platform.max_image_count})"
        })

    # 如果有其他特定平台验证规则
    if hasattr(platform, 'name'):
        # 某些平台的特殊验证
        if platform.name == "知乎":
            # 知乎特殊规则示例
            pass
        elif platform.name == "微信公众号":
            # 微信公众号特殊规则示例
            pass

    # 设置验证结果
    has_error = any(not detail.get('valid', True) for detail in details)
    result["valid"] = not has_error
    result["details"] = details

    if has_error:
        result["message"] = "文章不符合平台要求，请查看详细信息"

    return result
