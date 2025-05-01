"""
临时大纲存储集成测试

测试临时大纲存储的实际功能，包括创建、保存、获取、更新和删除临时大纲。
"""

import pytest
from datetime import datetime

from core.models.outline.basic_outline import BasicOutline, OutlineNode
from core.models.outline.outline_storage import OutlineStorage


class TestTempOutlineIntegration:
    """临时大纲存储集成测试"""

    def setup_method(self):
        """测试前设置"""
        # 初始化存储
        OutlineStorage.initialize()
        
        # 清理可能存在的测试数据
        for outline_id in OutlineStorage.list_outlines():
            if outline_id.startswith("test_"):
                OutlineStorage.delete_outline(outline_id)

    def teardown_method(self):
        """测试后清理"""
        # 清理测试数据
        for outline_id in OutlineStorage.list_outlines():
            if outline_id.startswith("test_"):
                OutlineStorage.delete_outline(outline_id)

    def test_save_and_get_outline(self):
        """测试保存和获取大纲"""
        # 创建大纲
        outline = BasicOutline(
            title="测试临时大纲",
            description="这是一个测试用的临时大纲",
            content_type="article",
            nodes=[
                OutlineNode(
                    title="第一章",
                    content="这是第一章的内容",
                    level=1
                )
            ]
        )
        
        # 保存大纲
        outline_id = "test_outline_001"
        saved_id = OutlineStorage.save_outline(outline, outline_id)
        
        # 验证保存结果
        assert saved_id == outline_id
        
        # 获取大纲
        retrieved_outline = OutlineStorage.get_outline(outline_id)
        
        # 验证获取结果
        assert retrieved_outline is not None
        assert retrieved_outline.title == "测试临时大纲"
        assert retrieved_outline.description == "这是一个测试用的临时大纲"
        assert retrieved_outline.content_type == "article"
        assert len(retrieved_outline.nodes) == 1
        assert retrieved_outline.nodes[0].title == "第一章"
        assert retrieved_outline.nodes[0].content == "这是第一章的内容"

    def test_update_outline(self):
        """测试更新大纲"""
        # 创建大纲
        outline = BasicOutline(
            title="测试临时大纲",
            description="这是一个测试用的临时大纲",
            content_type="article",
            nodes=[
                OutlineNode(
                    title="第一章",
                    content="这是第一章的内容",
                    level=1
                )
            ]
        )
        
        # 保存大纲
        outline_id = "test_outline_002"
        OutlineStorage.save_outline(outline, outline_id)
        
        # 获取大纲
        retrieved_outline = OutlineStorage.get_outline(outline_id)
        
        # 修改大纲
        retrieved_outline.title = "更新后的临时大纲"
        retrieved_outline.description = "这是更新后的描述"
        retrieved_outline.nodes.append(
            OutlineNode(
                title="第二章",
                content="这是第二章的内容",
                level=1
            )
        )
        
        # 更新大纲
        update_result = OutlineStorage.update_outline(outline_id, retrieved_outline)
        
        # 验证更新结果
        assert update_result is True
        
        # 再次获取大纲
        updated_outline = OutlineStorage.get_outline(outline_id)
        
        # 验证更新后的大纲
        assert updated_outline.title == "更新后的临时大纲"
        assert updated_outline.description == "这是更新后的描述"
        assert len(updated_outline.nodes) == 2
        assert updated_outline.nodes[1].title == "第二章"

    def test_delete_outline(self):
        """测试删除大纲"""
        # 创建大纲
        outline = BasicOutline(
            title="测试临时大纲",
            content_type="article"
        )
        
        # 保存大纲
        outline_id = "test_outline_003"
        OutlineStorage.save_outline(outline, outline_id)
        
        # 验证大纲存在
        assert OutlineStorage.get_outline(outline_id) is not None
        
        # 删除大纲
        delete_result = OutlineStorage.delete_outline(outline_id)
        
        # 验证删除结果
        assert delete_result is True
        
        # 验证大纲不存在
        assert OutlineStorage.get_outline(outline_id) is None

    def test_list_outlines(self):
        """测试列出所有大纲"""
        # 创建多个大纲
        outlines = [
            BasicOutline(title="测试临时大纲1", content_type="article"),
            BasicOutline(title="测试临时大纲2", content_type="article"),
            BasicOutline(title="测试临时大纲3", content_type="article")
        ]
        
        # 保存大纲
        outline_ids = []
        for i, outline in enumerate(outlines):
            outline_id = f"test_outline_{i+1:03d}"
            OutlineStorage.save_outline(outline, outline_id)
            outline_ids.append(outline_id)
        
        # 获取所有大纲ID
        all_ids = OutlineStorage.list_outlines()
        
        # 验证所有测试大纲ID都在列表中
        for outline_id in outline_ids:
            assert outline_id in all_ids

    def test_save_outline_with_dict(self):
        """测试保存字典形式的大纲"""
        # 创建大纲字典
        outline_dict = {
            "title": "字典形式的临时大纲",
            "description": "这是一个以字典形式创建的临时大纲",
            "content_type": "article",
            "nodes": [
                {
                    "title": "第一章",
                    "content": "这是第一章的内容",
                    "level": 1
                }
            ]
        }
        
        # 保存大纲
        outline_id = "test_outline_dict"
        saved_id = OutlineStorage.save_outline(outline_dict, outline_id)
        
        # 验证保存结果
        assert saved_id == outline_id
        
        # 获取大纲
        retrieved_outline = OutlineStorage.get_outline(outline_id)
        
        # 验证获取结果
        assert retrieved_outline is not None
        assert retrieved_outline.title == "字典形式的临时大纲"
        assert retrieved_outline.description == "这是一个以字典形式创建的临时大纲"
        assert retrieved_outline.content_type == "article"
        assert len(retrieved_outline.nodes) == 1
        assert retrieved_outline.nodes[0].title == "第一章"

    def test_auto_generate_id(self):
        """测试自动生成ID"""
        # 创建大纲
        outline = BasicOutline(
            title="自动ID临时大纲",
            content_type="article"
        )
        
        # 保存大纲，不提供ID
        outline_id = OutlineStorage.save_outline(outline)
        
        # 验证生成了ID
        assert outline_id is not None
        assert len(outline_id) > 0
        
        # 验证可以获取大纲
        retrieved_outline = OutlineStorage.get_outline(outline_id)
        assert retrieved_outline is not None
        assert retrieved_outline.title == "自动ID临时大纲"