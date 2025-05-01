"""
模型测试的配置文件

提供模型测试所需的夹具和模拟对象
"""
import sys
import pytest
from unittest.mock import MagicMock, patch

# 模型测试特定的模拟对象和夹具
# 这些模拟对象会覆盖全局conftest.py中定义的模拟对象

# 文章模型相关模拟
@pytest.fixture(scope="function")
def mock_article():
    """提供模拟的文章对象"""
    # Attempt to import test-specific Article model if it exists
    try:
        from tests.models.test_article import Article, Section
    except ImportError:
        # Fallback if test_article doesn't exist or define these
        Article = MagicMock()
        Section = MagicMock()

    # 创建基本章节
    section = Section(
        id="section_1",
        title="测试章节",
        content="这是测试章节的内容",
        order=1
    )

    # 创建文章
    article = Article(
        id="test_article_1",
        topic_id="test_topic",
        title="测试文章",
        summary="这是一篇测试文章",
        sections=[section]
    )

    return article

# Remove mock_config_service fixture as the service is deleted
# @pytest.fixture(scope="function")
# def mock_config_service():
#     """提供模拟的ConfigService对象"""
#     mock_service = MagicMock()
#     mock_service.get_config.return_value = {}
#     return mock_service

@pytest.fixture(scope="function")
def mock_redis_client():
    """提供模拟的Redis客户端"""
    mock_client = MagicMock()
    mock_client.get.return_value = None
    mock_client.set.return_value = True
    return mock_client

# Remove mock_db_adapter fixture as the adapter is deleted
# @pytest.fixture(scope="function")
# def mock_db_adapter():
#     """提供模拟的数据库适配器"""
#     mock_adapter = MagicMock()
#     mock_adapter.find_one.return_value = None
#     mock_adapter.insert_one.return_value = {"inserted_id": "test_id"}
#     mock_adapter.update_one.return_value = {"modified_count": 1}
#     return mock_adapter

@pytest.fixture(scope="function")
def mock_json_model_loader():
    """提供模拟的JsonModelLoader对象"""
    mock_loader = MagicMock()
    # Make load methods return empty list/None by default
    mock_loader.load_models_from_directory.return_value = []
    mock_loader.load_model_from_file.return_value = None
    return mock_loader
