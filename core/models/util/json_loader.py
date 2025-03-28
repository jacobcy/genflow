"""JSON模型加载器

用于从JSON文件加载和管理配置数据的工具，支持单文件加载和目录批量加载。
"""

from typing import Dict, Any, Optional, List, Type, TypeVar, Generic
import json
import os
import glob
from pathlib import Path
from loguru import logger

# 泛型类型变量，用于类型提示
T = TypeVar('T')

class JsonModelLoader(Generic[T]):
    """通用 JSON 配置加载器

    用于从特定目录加载 JSON 配置文件并转换为 Pydantic 模型
    """

    @staticmethod
    def load_model(json_path: str, model_class: Type[T]) -> Optional[T]:
        """从 JSON 文件加载单个模型

        Args:
            json_path: JSON 文件路径
            model_class: Pydantic 模型类

        Returns:
            Optional[T]: 模型实例，如果加载失败则返回 None
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return model_class(**data)
        except Exception as e:
            logger.error(f"加载 JSON 文件 {json_path} 失败: {str(e)}")
            return None

    @staticmethod
    def load_models_from_directory(directory: str, model_class: Type[T]) -> Dict[str, T]:
        """从目录加载多个模型

        Args:
            directory: 包含 JSON 文件的目录路径
            model_class: Pydantic 模型类

        Returns:
            Dict[str, T]: 模型字典，键为模型 ID
        """
        results = {}

        # 确保目录存在
        if not os.path.exists(directory):
            logger.warning(f"目录 {directory} 不存在")
            return results

        # 加载目录中的所有 JSON 文件
        json_files = glob.glob(os.path.join(directory, '*.json'))
        for json_file in json_files:
            try:
                model_instance = JsonModelLoader.load_model(json_file, model_class)
                if model_instance:
                    # 使用文件名（不含扩展名）作为键名，除非模型有 id 属性
                    model_id = getattr(model_instance, 'id', Path(json_file).stem)
                    results[model_id] = model_instance
            except Exception as e:
                logger.error(f"处理 {json_file} 时出错: {str(e)}")

        return results

    @staticmethod
    def get_base_directory() -> str:
        """获取模型基础目录

        Returns:
            str: 基础目录路径
        """
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return current_dir
