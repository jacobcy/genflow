"""JSON模型加载器

提供从目录加载JSON模型文件的功能。
"""

import os
import json
from typing import List, Dict, Any, Type, TypeVar, Optional, cast, Union, Callable
from pathlib import Path
from loguru import logger
from pydantic import BaseModel

# Default config directory (relative to project root usually)
# Determine project root dynamically or use environment variable
# Assuming project root is 4 levels up from this file's directory for now
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CONFIG_DIR = Path(os.environ.get(
    "GENFLOW_CONFIG_DIR",
    PROJECT_ROOT / "config"
))

def get_config_file_path(config_type: str, filename: str) -> Path:
    """获取标准配置文件的绝对路径

    Args:
        config_type: 配置类型目录名 (e.g., "styles", "platforms")
        filename: 配置文件名 (e.g., "article_styles.json")

    Returns:
        Path: 配置文件的绝对路径对象
    """
    return CONFIG_DIR / config_type / filename

def load_json_config(config_path: Path) -> Optional[Dict[str, Any]]:
    """从指定路径加载JSON配置文件

    Args:
        config_path: 配置文件的绝对路径

    Returns:
        Optional[Dict[str, Any]]: 加载的配置字典，如果文件不存在或解析失败则返回 None
    """
    if not isinstance(config_path, Path):
        config_path = Path(config_path)

    if not config_path.is_file():
        logger.warning(f"配置文件不存在: {config_path}")
        return None
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.debug(f"成功加载配置文件: {config_path}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"解析JSON配置文件失败: {config_path}, 错误: {e}")
        return None
    except Exception as e:
        logger.error(f"加载配置文件时发生未知错误: {config_path}, 错误: {e}")
        return None

T = TypeVar('T')

class JsonModelLoader:
    """JSON模型加载器，用于从文件目录加载模型"""

    @staticmethod
    def load_models_from_directory(directory: str, model_class: Type[T]) -> List[T]:
        """从目录加载模型

        Args:
            directory: 目录路径
            model_class: 模型类

        Returns:
            List[T]: 模型对象列表
        """
        models: List[T] = []

        # 检查目录是否存在
        if not os.path.exists(directory):
            logger.warning(f"目录不存在: {directory}")
            return models

        # 遍历目录中的所有JSON文件
        for file_path in Path(directory).glob("*.json"):
            try:
                # 读取JSON文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 如果model_class是BaseModel的子类，使用其构造函数
                if isinstance(model_class, type) and issubclass(model_class, BaseModel):
                    # 对于Pydantic模型，直接使用**data初始化
                    model = cast(T, model_class(**data))
                # 如果model_class是dict类型，直接返回字典
                elif model_class == dict:
                    model = cast(T, data)
                # 其他情况，尝试直接实例化
                else:
                    try:
                        # 尝试使用空构造函数创建实例，然后设置属性
                        model_instance = model_class()
                        for key, value in data.items():
                            if hasattr(model_instance, key):
                                setattr(model_instance, key, value)
                        model = cast(T, model_instance)
                    except Exception:
                        # 失败时使用字典作为回退
                        model = cast(T, data)

                models.append(model)
                logger.debug(f"已加载模型: {file_path.name}")
            except Exception as e:
                logger.error(f"加载模型失败 {file_path}: {str(e)}")

        return models

    @staticmethod
    def load_model_from_file(file_path: str, model_class: Type[T]) -> Optional[T]:
        """从文件加载模型

        Args:
            file_path: 文件路径
            model_class: 模型类

        Returns:
            Optional[T]: 模型对象，失败则返回None
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.warning(f"文件不存在: {file_path}")
                return None

            # 读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 如果model_class是BaseModel的子类，使用其构造函数
            if isinstance(model_class, type) and issubclass(model_class, BaseModel):
                # 对于Pydantic模型，直接使用**data初始化
                model = cast(T, model_class(**data))
            # 如果model_class是dict类型，直接返回字典
            elif model_class == dict:
                model = cast(T, data)
            # 其他情况，尝试直接实例化
            else:
                try:
                    # 尝试使用空构造函数创建实例，然后设置属性
                    model_instance = model_class()
                    for key, value in data.items():
                        if hasattr(model_instance, key):
                            setattr(model_instance, key, value)
                    model = cast(T, model_instance)
                except Exception:
                    # 失败时使用字典作为回退
                    model = cast(T, data)

            logger.debug(f"已加载模型: {file_path}")
            return model
        except Exception as e:
            logger.error(f"加载模型失败 {file_path}: {str(e)}")
            return None

    @staticmethod
    def save_model_to_file(model: Union[BaseModel, Dict[str, Any]], file_path: str) -> bool:
        """将模型保存到文件

        Args:
            model: 模型对象或字典
            file_path: 文件路径

        Returns:
            bool: 是否成功保存
        """
        try:
            # 创建目录（如果不存在）
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # 将模型转换为字典并保存
            with open(file_path, 'w', encoding='utf-8') as f:
                if isinstance(model, BaseModel):
                    # 对于Pydantic模型
                    if hasattr(model, 'dict') and callable(getattr(model, 'dict')):
                        # Pydantic V1
                        data = model.dict()
                    elif hasattr(model, 'model_dump') and callable(getattr(model, 'model_dump')):
                        # Pydantic V2
                        data = model.model_dump()
                    else:
                        # 使用__dict__作为回退
                        data = model.__dict__
                else:
                    # 如果已经是字典，直接使用
                    data = model

                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.debug(f"已保存模型: {file_path}")
            return True
        except Exception as e:
            logger.error(f"保存模型失败 {file_path}: {str(e)}")
            return False
