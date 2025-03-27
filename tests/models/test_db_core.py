"""
GenFlow 数据库核心功能测试

这个模块测试 GenFlow 数据库的核心功能，包括：
1. 通过 ContentManager 访问数据库
2. 获取内容类型、文章风格和平台配置
3. 查询各种配置项
"""

import os
import sys
import logging
import pytest
from loguru import logger

# 设置日志级别
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 确保可以导入核心模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models.content_manager import ContentManager

# 在所有测试前执行的初始化
@pytest.fixture(scope="module")
def content_manager():
    """初始化ContentManager并返回"""
    ContentManager.initialize(use_db=True)
    return ContentManager

# 测试数据库初始化
def test_initialization(content_manager):
    """测试数据库初始化"""
    logger.info("测试1: 初始化 ContentManager")
    assert content_manager._is_initialized == True
    logger.info("ContentManager 初始化完成")

# 测试获取内容类型
def test_get_content_types(content_manager):
    """测试获取内容类型"""
    logger.info("测试2: 获取内容类型")

    # 获取所有内容类型
    content_types = content_manager.get_all_content_types()
    logger.info(f"找到 {len(content_types)} 个内容类型")
    logger.info(f"内容类型列表: {list(content_types.keys())}")

    # 验证内容类型数量和类型
    assert len(content_types) > 0, "应至少有一个内容类型"
    assert isinstance(content_types, dict), "内容类型应为字典格式"

    # 获取单个内容类型
    if "blog" in content_types:
        blog_type = content_manager.get_content_type("blog")
        logger.info(f"博客内容类型名称: {blog_type.name}")
        logger.info(f"博客内容类型描述: {blog_type.description}")
        assert blog_type is not None, "应能获取到blog内容类型"
        assert blog_type.name, "内容类型应有名称"
    else:
        logger.warning("未找到'blog'内容类型")

# 测试获取文章风格
def test_get_article_styles(content_manager):
    """测试获取文章风格"""
    logger.info("测试3: 获取文章风格")

    # 获取所有文章风格
    styles = content_manager.get_all_article_styles()
    logger.info(f"找到 {len(styles)} 个文章风格")
    logger.info(f"文章风格列表: {list(styles.keys()) if styles else []}")

    # 验证文章风格数量和类型
    assert len(styles) > 0, "应至少有一个文章风格"
    assert isinstance(styles, dict), "文章风格应为字典格式"

    # 获取单个文章风格
    if styles and "wechat" in styles:
        wechat_style = content_manager.get_article_style("wechat")
        logger.info(f"微信风格名称: {wechat_style.name}")
        logger.info(f"微信风格描述: {wechat_style.description}")
        assert wechat_style is not None, "应能获取到wechat风格"
        assert wechat_style.name, "文章风格应有名称"

# 测试获取平台配置
def test_get_platforms(content_manager):
    """测试获取平台配置"""
    logger.info("测试4: 获取平台配置")

    # 获取所有平台
    platforms = content_manager.get_all_platforms()
    logger.info(f"找到 {len(platforms)} 个平台")
    logger.info(f"平台列表: {list(platforms.keys()) if platforms else []}")

    # 验证平台数量和类型
    assert len(platforms) > 0, "应至少有一个平台"
    assert isinstance(platforms, dict), "平台配置应为字典格式"

    # 获取单个平台
    if platforms and "weibo" in platforms:
        weibo_platform = content_manager.get_platform("weibo")
        logger.info(f"微博平台名称: {weibo_platform.name}")
        logger.info(f"微博平台描述: {weibo_platform.description}")
        assert weibo_platform is not None, "应能获取到weibo平台"
        assert weibo_platform.name, "平台应有名称"

# 测试获取内容类型详情
def test_get_content_type_details(content_manager):
    """测试获取内容类型详情"""
    logger.info("测试5: 获取内容类型详情")

    # 尝试获取几个不同的内容类型
    test_types = ["article", "blog", "tutorial"]
    found_count = 0

    for content_type_id in test_types:
        content_type = content_manager.get_content_type(content_type_id)
        if content_type:
            found_count += 1
            logger.info(f"内容类型: {content_type_id}")
            logger.info(f"  名称: {content_type.name}")
            logger.info(f"  描述: {content_type.description}")
            logger.info(f"  类别: {content_type.category}")
            logger.info(f"  格式: {content_type.format}")

            # 验证内容类型属性
            assert content_type.name, "内容类型应有名称"
            assert content_type.description, "内容类型应有描述"
        else:
            logger.warning(f"未找到内容类型: {content_type_id}")

    # 确保至少找到一个内容类型
    assert found_count > 0, "应至少找到一个测试内容类型"

# 测试数据库同步功能
def test_sync_configs(content_manager):
    """测试数据库同步功能"""
    logger.info("测试6: 数据库同步")

    # 执行增量同步
    logger.info("执行增量同步...")
    result = content_manager.sync_configs_to_db()
    logger.info(f"增量同步结果: {'成功' if result else '失败'}")

    # 验证同步结果
    assert result == True, "数据库增量同步应成功"
