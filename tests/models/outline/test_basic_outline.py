"""
测试 BasicOutline 模型

测试基础大纲模型的创建、属性和方法。
"""

# import pytest  # 不需要
from datetime import datetime

from core.models.outline.basic_outline import BasicOutline, OutlineNode


class TestBasicOutline:
    """测试 BasicOutline 类"""

    def test_create_basic_outline(self):
        """测试创建基础大纲"""
        # 创建大纲节点
        node1 = OutlineNode(
            title="第一章",
            content="这是第一章的内容",
            level=1
        )

        node2 = OutlineNode(
            title="第二章",
            content="这是第二章的内容",
            level=2
        )

        # 创建子节点
        subnode1 = OutlineNode(
            title="第一章第一节",
            content="这是第一章第一节的内容",
            level=2
        )

        # 添加子节点
        node1.children = [subnode1]

        # 创建大纲
        outline = BasicOutline(
            title="测试大纲",
            content_type="article",
            nodes=[node1, node2]
        )

        # 验证基本属性
        assert outline.title == "测试大纲"
        assert outline.content_type == "article"
        assert len(outline.nodes) == 2
        assert outline.nodes[0].title == "第一章"
        assert outline.nodes[1].title == "第二章"
        assert len(outline.nodes[0].children) == 1
        assert outline.nodes[0].children[0].title == "第一章第一节"
        assert isinstance(outline.created_at, datetime)
        assert isinstance(outline.updated_at, datetime)

    def test_create_empty_outline(self):
        """测试创建空大纲"""
        # 创建大纲
        outline = BasicOutline(
            title="空大纲",
            content_type="article"
        )

        # 验证基本属性
        assert outline.title == "空大纲"
        assert outline.content_type == "article"
        assert len(outline.nodes) == 0
        assert isinstance(outline.created_at, datetime)
        assert isinstance(outline.updated_at, datetime)

    def test_add_section(self):
        """测试添加章节"""
        # 创建大纲
        outline = BasicOutline(
            title="测试大纲",
            content_type="article"
        )

        # 创建节点
        node = OutlineNode(
            title="新章节",
            content="这是新章节的内容",
            level=1
        )

        # 添加节点
        outline.nodes.append(node)

        # 验证
        assert len(outline.nodes) == 1
        assert outline.nodes[0].title == "新章节"
        assert outline.nodes[0].content == "这是新章节的内容"

    def test_to_dict(self):
        """测试转换为字典"""
        # 创建大纲节点
        node = OutlineNode(
            title="第一章",
            content="这是第一章的内容",
            level=1
        )

        # 创建大纲
        outline = BasicOutline(
            title="测试大纲",
            content_type="article",
            nodes=[node]
        )

        # 转换为字典
        result = outline.to_dict()

        # 验证
        assert result["title"] == "测试大纲"
        assert result["content_type"] == "article"
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["title"] == "第一章"
        assert result["nodes"][0]["content"] == "这是第一章的内容"
        assert "created_at" in result
        assert "updated_at" in result

    def test_from_dict(self):
        """测试从字典创建"""
        # 创建字典
        data = {
            "title": "字典大纲",
            "content_type": "article",
            "nodes": [
                {
                    "title": "第一章",
                    "content": "这是第一章的内容",
                    "level": 1,
                    "children": [
                        {
                            "title": "第一节",
                            "content": "这是第一节的内容",
                            "level": 1
                        }
                    ]
                }
            ]
        }

        # 从字典创建
        outline = BasicOutline.from_dict(data)

        # 验证
        assert outline.title == "字典大纲"
        assert outline.content_type == "article"
        assert len(outline.nodes) == 1
        assert outline.nodes[0].title == "第一章"
        assert len(outline.nodes[0].children) == 1
        assert outline.nodes[0].children[0].title == "第一节"

    def test_update_timestamp(self):
        """测试更新时间戳"""
        # 创建大纲
        outline = BasicOutline(
            title="测试大纲",
            content_type="article"
        )

        # 记录原始时间
        original_time = outline.updated_at

        # 等待一小段时间
        import time
        time.sleep(0.01)

        # 更新时间戳
        outline.updated_at = datetime.now()

        # 验证
        assert outline.updated_at > original_time


class TestOutlineNode:
    """测试 OutlineNode 类"""

    def test_create_node(self):
        """测试创建节点"""
        # 创建节点
        node = OutlineNode(
            title="测试节点",
            content="这是测试节点的内容",
            level=1
        )

        # 验证
        assert node.title == "测试节点"
        assert node.content == "这是测试节点的内容"
        assert node.level == 1
        assert len(node.children) == 0

    def test_add_child(self):
        """测试添加子节点"""
        # 创建父节点
        parent = OutlineNode(
            title="父节点",
            content="这是父节点的内容",
            level=1
        )

        # 创建子节点
        child = OutlineNode(
            title="子节点",
            content="这是子节点的内容",
            level=1
        )

        # 添加子节点
        parent.children.append(child)

        # 验证
        assert len(parent.children) == 1
        assert parent.children[0].title == "子节点"
        assert parent.children[0].content == "这是子节点的内容"

    def test_to_dict(self):
        """测试转换为字典"""
        # 创建节点
        node = OutlineNode(
            title="测试节点",
            content="这是测试节点的内容",
            level=1
        )

        # 创建子节点
        child = OutlineNode(
            title="子节点",
            content="这是子节点的内容",
            level=1
        )

        # 添加子节点
        node.children.append(child)

        # 转换为字典
        result = node.model_dump()

        # 验证
        assert result["title"] == "测试节点"
        assert result["content"] == "这是测试节点的内容"
        assert result["level"] == 1
        assert len(result["children"]) == 1
        assert result["children"][0]["title"] == "子节点"

    def test_from_dict(self):
        """测试从字典创建"""
        # 创建字典
        data = {
            "title": "字典节点",
            "content": "这是字典节点的内容",
            "level": 2,
            "children": [
                {
                    "title": "子节点",
                    "content": "这是子节点的内容",
                    "level": 1
                }
            ]
        }

        # 从字典创建
        node = OutlineNode.model_validate(data)

        # 验证
        assert node.title == "字典节点"
        assert node.content == "这是字典节点的内容"
        assert node.level == 2
        assert len(node.children) == 1
        assert node.children[0].title == "子节点"