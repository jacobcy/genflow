"""测试内容类型配置

验证内容类型配置文件的格式和数据是否符合模型要求。
测试新的基于目录的内容类型配置。
"""

import json
import os
import unittest
from pathlib import Path
from typing import Dict, List, Set

class TestContentTypes(unittest.TestCase):
    """内容类型配置测试"""

    @classmethod
    def setUpClass(cls):
        """加载配置文件"""
        config_dir = Path(__file__).parent.parent / "core" / "models" / "content_types"
        cls.config_files = list(config_dir.glob("*.json"))
        cls.configs = {}

        # 加载所有JSON配置文件
        for file_path in cls.config_files:
            if file_path.name == "category_mapping.json":
                with open(file_path, "r", encoding="utf-8") as f:
                    cls.category_mapping = json.load(f)
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    content_type_id = file_path.stem
                    cls.configs[content_type_id] = json.load(f)

    def test_config_structure(self):
        """测试配置文件结构"""
        # 验证配置文件数量
        self.assertGreater(len(self.configs), 8, "配置文件数量不足")

        # 验证每个内容类型配置的必要字段
        required_fields = {
            "id", "name", "category", "description", "format", "primary_purpose",
            "structure_templates", "format_guidelines", "characteristics",
            "compatible_styles", "example_topics", "metadata"
        }

        for content_type_id, config in self.configs.items():
            self.assertEqual(
                config["id"],
                content_type_id,
                f"内容类型 '{content_type_id}' 的ID与文件名不匹配"
            )

            missing_fields = required_fields - set(config.keys())
            self.assertEqual(
                len(missing_fields),
                0,
                f"内容类型 '{content_type_id}' 缺少必要字段: {missing_fields}"
            )

    def test_content_type_consistency(self):
        """测试内容类型一致性"""
        # 验证是否存在类别映射配置
        self.assertIsNotNone(
            getattr(self, "category_mapping", None),
            "找不到类别映射配置"
        )

        if hasattr(self, "category_mapping"):
            # 验证类别映射中的内容类型是否存在对应配置文件
            category_mapping = self.category_mapping.get("category_mapping", {})
            content_type_groups = self.category_mapping.get("content_type_groups", {})

            # 验证类别映射中的内容类型是否都有配置
            for category, mapped_type in category_mapping.items():
                self.assertIn(
                    mapped_type,
                    self.configs,
                    f"类别 '{category}' 映射到了不存在的内容类型 '{mapped_type}'"
                )

            # 验证内容类型分组中的类型是否都有配置
            for group_name, types in content_type_groups.items():
                for content_type in types:
                    # 直接检查内容类型ID是否存在
                    self.assertIn(
                        content_type,
                        self.configs,
                        f"内容类型分组 '{group_name}' 包含不存在的内容类型 '{content_type}'"
                    )

    def test_format_guidelines_structure(self):
        """测试格式指南结构"""
        required_fields = {
            "min_length", "max_length", "min_section_count", "max_section_count",
            "recommended_section_length", "title_guidelines", "requires_images", "requires_code"
        }

        for content_type_id, config in self.configs.items():
            format_guidelines = config.get("format_guidelines", {})
            missing_fields = required_fields - set(format_guidelines.keys())
            self.assertEqual(
                len(missing_fields),
                0,
                f"内容类型 '{content_type_id}' 的格式指南缺少必要字段: {missing_fields}"
            )

            # 验证字段类型
            self.assertIsInstance(format_guidelines["min_length"], int, f"内容类型 '{content_type_id}' 的最小长度必须是整数")
            self.assertIsInstance(format_guidelines["max_length"], int, f"内容类型 '{content_type_id}' 的最大长度必须是整数")
            self.assertIsInstance(format_guidelines["min_section_count"], int, f"内容类型 '{content_type_id}' 的最小章节数必须是整数")
            self.assertIsInstance(format_guidelines["max_section_count"], int, f"内容类型 '{content_type_id}' 的最大章节数必须是整数")
            self.assertIsInstance(format_guidelines["recommended_section_length"], int, f"内容类型 '{content_type_id}' 的推荐章节长度必须是整数")
            self.assertIsInstance(format_guidelines["title_guidelines"], dict, f"内容类型 '{content_type_id}' 的标题指南必须是字典")
            self.assertIsInstance(format_guidelines["requires_images"], bool, f"内容类型 '{content_type_id}' 的图片需求必须是布尔值")
            self.assertIsInstance(format_guidelines["requires_code"], bool, f"内容类型 '{content_type_id}' 的代码需求必须是布尔值")

    def test_characteristics_structure(self):
        """测试内容特性结构"""
        required_fields = {
            "is_technical", "is_creative", "is_formal", "is_timely",
            "is_narrative", "is_instructional", "audience_level",
            "multimedia_focus", "research_intensity"
        }

        for content_type_id, config in self.configs.items():
            characteristics = config.get("characteristics", {})
            missing_fields = required_fields - set(characteristics.keys())
            self.assertEqual(
                len(missing_fields),
                0,
                f"内容类型 '{content_type_id}' 的内容特性缺少必要字段: {missing_fields}"
            )

            # 验证字段类型
            self.assertIsInstance(characteristics["is_technical"], bool, f"内容类型 '{content_type_id}' 的技术性必须是布尔值")
            self.assertIsInstance(characteristics["is_creative"], bool, f"内容类型 '{content_type_id}' 的创意性必须是布尔值")
            self.assertIsInstance(characteristics["is_formal"], bool, f"内容类型 '{content_type_id}' 的正式性必须是布尔值")
            self.assertIsInstance(characteristics["is_timely"], bool, f"内容类型 '{content_type_id}' 的时效性必须是布尔值")
            self.assertIsInstance(characteristics["is_narrative"], bool, f"内容类型 '{content_type_id}' 的叙事性必须是布尔值")
            self.assertIsInstance(characteristics["is_instructional"], bool, f"内容类型 '{content_type_id}' 的教学性必须是布尔值")
            self.assertIsInstance(characteristics["audience_level"], str, f"内容类型 '{content_type_id}' 的受众水平必须是字符串")
            self.assertIsInstance(characteristics["multimedia_focus"], bool, f"内容类型 '{content_type_id}' 的多媒体焦点必须是布尔值")
            self.assertIsInstance(characteristics["research_intensity"], int, f"内容类型 '{content_type_id}' 的研究强度必须是整数")

            # 验证研究强度范围
            self.assertGreaterEqual(characteristics["research_intensity"], 1, f"内容类型 '{content_type_id}' 的研究强度必须大于等于1")
            self.assertLessEqual(characteristics["research_intensity"], 5, f"内容类型 '{content_type_id}' 的研究强度必须小于等于5")

    def test_structure_templates(self):
        """测试结构模板"""
        for content_type_id, config in self.configs.items():
            templates = config.get("structure_templates", [])
            self.assertGreater(len(templates), 0, f"内容类型 '{content_type_id}' 必须至少有一个结构模板")

            for template in templates:
                required_fields = {"name", "description", "sections", "outline_template", "examples"}
                missing_fields = required_fields - set(template.keys())
                self.assertEqual(
                    len(missing_fields),
                    0,
                    f"内容类型 '{content_type_id}' 的结构模板缺少必要字段: {missing_fields}"
                )

                # 验证字段类型
                self.assertIsInstance(template["name"], str, f"内容类型 '{content_type_id}' 的模板名称必须是字符串")
                self.assertIsInstance(template["description"], str, f"内容类型 '{content_type_id}' 的模板描述必须是字符串")
                self.assertIsInstance(template["sections"], list, f"内容类型 '{content_type_id}' 的章节列表必须是列表")
                self.assertIsInstance(template["outline_template"], dict, f"内容类型 '{content_type_id}' 的大纲模板必须是字典")
                self.assertIsInstance(template["examples"], list, f"内容类型 '{content_type_id}' 的示例必须是列表")

                # 验证章节列表和大纲模板的一致性
                self.assertGreater(len(template["sections"]), 0, f"内容类型 '{content_type_id}' 的章节列表不能为空")
                # 大纲模板可以更详细，不必严格一致

    def test_program_load_compatibility(self):
        """测试通过编程方式加载配置的兼容性"""
        # 动态导入以避免循环引用问题
        import importlib
        module = importlib.import_module('core.models.content_manager')
        ContentManager = getattr(module, 'ContentManager')

        # 初始化管理器
        ContentManager.initialize()

        # 获取所有内容类型
        content_types = ContentManager.get_all_content_types()
        self.assertGreater(len(content_types), 0, "无法通过管理器加载内容类型")

        # 验证每个内容类型是否可以通过管理器获取
        for content_type_id in self.configs.keys():
            content_type = ContentManager.get_content_type(content_type_id)
            self.assertIsNotNone(content_type, f"无法通过管理器获取内容类型 '{content_type_id}'")
            self.assertEqual(content_type.id, content_type_id, f"内容类型ID不匹配: {content_type.id} != {content_type_id}")

        # 验证类别映射
        if hasattr(self, "category_mapping"):
            category_mapping = self.category_mapping.get("category_mapping", {})
            for category, mapped_type in list(category_mapping.items())[:5]:  # 测试前5个
                content_type = ContentManager.get_content_type_by_category(category)
                self.assertIsNotNone(content_type, f"无法通过类别 '{category}' 获取内容类型")
                self.assertEqual(content_type.id, mapped_type, f"通过类别获取的内容类型与映射不匹配")

if __name__ == "__main__":
    unittest.main()
