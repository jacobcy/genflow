"""内容管理器测试脚本

验证优化后的ContentManager是否正常工作
"""

import sys
import os
import unittest
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# 导入被测试组件
from core.models.content_manager import ContentManager
from core.models.topic.topic import Topic


class ContentManagerTest(unittest.TestCase):
    """内容管理器测试类"""

    def setUp(self):
        """测试准备"""
        # 初始化内容管理器
        ContentManager.initialize(use_db=False)

    def test_create_and_save_topic(self):
        """测试创建和保存话题"""
        # 创建话题
        title = "测试话题"
        keywords = ["测试", "话题"]
        topic = ContentManager.create_topic(title, keywords)

        # 断言话题创建成功
        self.assertIsNotNone(topic)
        # 检查类型并访问属性
        if topic is not None:
            self.assertEqual(topic.title, title)
            self.assertEqual(topic.keywords, keywords)
            topic_id = topic.id

            # 获取话题
            retrieved_topic = ContentManager.get_topic(topic_id)
            self.assertIsNotNone(retrieved_topic)
            if retrieved_topic is not None:
                self.assertEqual(retrieved_topic.id, topic_id)
                self.assertEqual(retrieved_topic.title, title)

    def test_create_and_save_basic_research(self):
        """测试创建和保存基础研究"""
        # 创建基础研究
        title = "测试研究"
        research = ContentManager.create_basic_research(
            title=title,
            keywords=["测试", "研究"],
            content="这是一个测试研究内容",
            metadata={"test_key": "test_value"}
        )

        # 断言研究创建成功
        self.assertIsNotNone(research)
        if research is not None:
            self.assertEqual(research.title, title)

            # 保存研究
            result = ContentManager.save_basic_research(research)
            self.assertTrue(result)

            # 从metadata获取ID
            if hasattr(research, 'metadata') and research.metadata is not None:
                research_id = research.metadata.get("research_id")
                self.assertIsNotNone(research_id)

                # 获取研究
                retrieved_research = ContentManager.get_basic_research(research_id)
                self.assertIsNotNone(retrieved_research)
                if retrieved_research is not None:
                    self.assertEqual(retrieved_research.title, title)

    def test_article_style(self):
        """测试文章风格功能"""
        # 获取所有风格
        styles = ContentManager.get_all_styles()
        self.assertIsNotNone(styles)

        # 获取默认风格
        default_style = ContentManager.get_default_style()
        self.assertIsNotNone(default_style)


if __name__ == "__main__":
    unittest.main()
