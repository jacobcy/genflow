"""
临时研究存储集成测试

测试临时研究存储的实际功能，包括创建、保存、获取、更新和删除临时研究。
"""

import pytest
from datetime import datetime

from core.models.research.basic_research import BasicResearch, KeyFinding, Source
from core.models.research.research_storage import ResearchStorage


class TestTempResearchIntegration:
    """临时研究存储集成测试"""

    def setup_method(self):
        """测试前设置"""
        # 初始化存储
        ResearchStorage.initialize()

        # 清理可能存在的测试数据
        for research_id in ResearchStorage.list_researches():
            if research_id.startswith("test_"):
                ResearchStorage.delete_research(research_id)

    def teardown_method(self):
        """测试后清理"""
        # 清理测试数据
        for research_id in ResearchStorage.list_researches():
            if research_id.startswith("test_"):
                ResearchStorage.delete_research(research_id)

    def test_save_and_get_research(self):
        """测试保存和获取研究"""
        # 创建研究
        research = BasicResearch(
            title="测试临时研究",
            background="这是一个测试用的临时研究",
            content_type="article",
            key_findings=[
                KeyFinding(
                    content="这是一个关键发现",
                    importance=0.8
                )
            ]
        )

        # 保存研究
        research_id = "test_research_001"
        saved_id = ResearchStorage.save_research(research, research_id)

        # 验证保存结果
        assert saved_id == research_id

        # 获取研究
        retrieved_research = ResearchStorage.get_research(research_id)

        # 验证获取结果
        assert retrieved_research is not None
        assert retrieved_research.title == "测试临时研究"
        assert retrieved_research.background == "这是一个测试用的临时研究"
        assert retrieved_research.content_type == "article"
        assert len(retrieved_research.key_findings) == 1
        assert retrieved_research.key_findings[0].content == "这是一个关键发现"
        assert retrieved_research.key_findings[0].importance == 0.8

    def test_update_research(self):
        """测试更新研究"""
        # 创建研究
        research = BasicResearch(
            title="测试临时研究",
            background="这是一个测试用的临时研究",
            content_type="article",
            key_findings=[
                KeyFinding(
                    content="这是一个关键发现",
                    importance=0.8
                )
            ]
        )

        # 保存研究
        research_id = "test_research_002"
        ResearchStorage.save_research(research, research_id)

        # 获取研究
        retrieved_research = ResearchStorage.get_research(research_id)

        # 修改研究
        retrieved_research.title = "更新后的临时研究"
        retrieved_research.background = "这是更新后的背景"
        retrieved_research.key_findings.append(
            KeyFinding(
                content="这是另一个关键发现",
                importance=0.9
            )
        )

        # 更新研究
        update_result = ResearchStorage.update_research(research_id, retrieved_research)

        # 验证更新结果
        assert update_result is True

        # 再次获取研究
        updated_research = ResearchStorage.get_research(research_id)

        # 验证更新后的研究
        assert updated_research.title == "更新后的临时研究"
        assert updated_research.background == "这是更新后的背景"
        assert len(updated_research.key_findings) == 2
        assert updated_research.key_findings[1].content == "这是另一个关键发现"

    def test_delete_research(self):
        """测试删除研究"""
        # 创建研究
        research = BasicResearch(
            title="测试临时研究",
            content_type="article"
        )

        # 保存研究
        research_id = "test_research_003"
        ResearchStorage.save_research(research, research_id)

        # 验证研究存在
        assert ResearchStorage.get_research(research_id) is not None

        # 删除研究
        delete_result = ResearchStorage.delete_research(research_id)

        # 验证删除结果
        assert delete_result is True

        # 验证研究不存在
        assert ResearchStorage.get_research(research_id) is None

    def test_list_researches(self):
        """测试列出所有研究"""
        # 创建多个研究
        researches = [
            BasicResearch(title="测试临时研究1", content_type="article"),
            BasicResearch(title="测试临时研究2", content_type="article"),
            BasicResearch(title="测试临时研究3", content_type="article")
        ]

        # 保存研究
        research_ids = []
        for i, research in enumerate(researches):
            research_id = f"test_research_{i+1:03d}"
            ResearchStorage.save_research(research, research_id)
            research_ids.append(research_id)

        # 获取所有研究ID
        all_ids = ResearchStorage.list_researches()

        # 验证所有测试研究ID都在列表中
        for research_id in research_ids:
            assert research_id in all_ids

    def test_save_research_with_dict(self):
        """测试保存字典形式的研究"""
        # 创建研究字典
        research_dict = {
            "title": "字典形式的临时研究",
            "background": "这是一个以字典形式创建的临时研究",
            "content_type": "article",
            "key_findings": [
                {
                    "content": "这是一个关键发现",
                    "importance": 0.8
                }
            ]
        }

        # 保存研究
        research_id = "test_research_dict"
        saved_id = ResearchStorage.save_research(research_dict, research_id)

        # 验证保存结果
        assert saved_id == research_id

        # 获取研究
        retrieved_research = ResearchStorage.get_research(research_id)

        # 验证获取结果
        assert retrieved_research is not None
        assert retrieved_research.title == "字典形式的临时研究"
        assert retrieved_research.background == "这是一个以字典形式创建的临时研究"
        assert retrieved_research.content_type == "article"
        assert len(retrieved_research.key_findings) == 1
        assert retrieved_research.key_findings[0].content == "这是一个关键发现"

    def test_auto_generate_id(self):
        """测试自动生成ID"""
        # 创建研究
        research = BasicResearch(
            title="自动ID临时研究",
            content_type="article"
        )

        # 保存研究，不提供ID
        research_id = ResearchStorage.save_research(research)

        # 验证生成了ID
        assert research_id is not None
        assert len(research_id) > 0

        # 验证可以获取研究
        retrieved_research = ResearchStorage.get_research(research_id)
        assert retrieved_research is not None
        assert retrieved_research.title == "自动ID临时研究"