"""临时存储管理器

该模块提供临时存储功能，用于存储生命周期短暂的对象，
例如临时大纲、进度报告等，这些对象不需要持久化到数据库。
"""

from typing import Dict, Optional, Any, TypeVar, Generic, List
from datetime import datetime, timedelta
import uuid
import threading
from loguru import logger

T = TypeVar('T')

class TemporaryStorage(Generic[T]):
    """通用临时存储类

    使用内存存储临时对象，支持过期时间和自动清理。
    """

    # 类变量，存储所有实例
    _instances: Dict[str, 'TemporaryStorage'] = {}
    _lock = threading.Lock()

    def __init__(self, name: str, ttl_seconds: int = 3600):
        """初始化临时存储

        Args:
            name: 存储名称，用于识别不同的存储实例
            ttl_seconds: 对象默认生存时间（秒），默认1小时
        """
        self.name = name
        self.ttl_seconds = ttl_seconds
        self.items: Dict[str, Dict[str, Any]] = {}
        self.last_cleanup = datetime.now()

    @classmethod
    def get_instance(cls, name: str, ttl_seconds: int = 3600) -> 'TemporaryStorage':
        """获取存储实例，如果不存在则创建

        Args:
            name: 存储名称
            ttl_seconds: 对象默认生存时间（秒）

        Returns:
            TemporaryStorage: 存储实例
        """
        with cls._lock:
            if name not in cls._instances:
                cls._instances[name] = TemporaryStorage(name, ttl_seconds)
            return cls._instances[name]

    def set(self, key: str, value: T, ttl_seconds: Optional[int] = None) -> str:
        """存储对象

        Args:
            key: 对象键名，如果为None则自动生成
            value: 要存储的对象
            ttl_seconds: 对象生存时间（秒），如果为None则使用默认值

        Returns:
            str: 存储的键名
        """
        # 如果没有提供key，生成唯一ID
        if key is None:
            key = str(uuid.uuid4())

        # 计算过期时间
        ttl = ttl_seconds if ttl_seconds is not None else self.ttl_seconds
        expiry = datetime.now() + timedelta(seconds=ttl)

        # 存储对象
        self.items[key] = {
            'value': value,
            'expiry': expiry,
            'created_at': datetime.now()
        }

        # 执行清理
        self._cleanup_if_needed()

        return key

    def get(self, key: str) -> Optional[T]:
        """获取对象

        Args:
            key: 对象键名

        Returns:
            Optional[T]: 存储的对象，如果不存在或已过期则返回None
        """
        # 执行清理
        self._cleanup_if_needed()

        # 检查对象是否存在
        if key not in self.items:
            return None

        # 检查对象是否过期
        item = self.items[key]
        if datetime.now() > item['expiry']:
            del self.items[key]
            return None

        return item['value']

    def update(self, key: str, value: T) -> bool:
        """更新对象，保持原有过期时间

        Args:
            key: 对象键名
            value: 新的对象值

        Returns:
            bool: 是否成功更新
        """
        if key not in self.items:
            return False

        # 保持原有过期时间
        expiry = self.items[key]['expiry']
        created_at = self.items[key]['created_at']

        # 更新对象
        self.items[key] = {
            'value': value,
            'expiry': expiry,
            'created_at': created_at
        }

        return True

    def delete(self, key: str) -> bool:
        """删除对象

        Args:
            key: 对象键名

        Returns:
            bool: 是否成功删除
        """
        if key not in self.items:
            return False

        del self.items[key]
        return True

    def list_keys(self) -> List[str]:
        """列出所有有效的键名

        Returns:
            List[str]: 键名列表
        """
        # 执行清理
        self._cleanup_if_needed()

        return list(self.items.keys())

    def _cleanup_if_needed(self) -> None:
        """根据需要执行清理，避免过于频繁的清理"""
        # 每10分钟或项目数超过100时执行一次完整清理
        current_time = datetime.now()
        if (current_time - self.last_cleanup > timedelta(minutes=10) or
                len(self.items) > 100):
            self._cleanup()
            self.last_cleanup = current_time

    def _cleanup(self) -> None:
        """清理过期对象"""
        current_time = datetime.now()
        expired_keys = [
            key for key, item in self.items.items()
            if current_time > item['expiry']
        ]

        for key in expired_keys:
            del self.items[key]

        if expired_keys:
            logger.debug(f"[{self.name}] 已清理 {len(expired_keys)} 个过期对象")


class OutlineStorage:
    """文章大纲临时存储类

    专门用于存储临时的文章大纲对象，不持久化到数据库。
    """

    # 默认TTL：2小时
    DEFAULT_TTL = 7200

    @classmethod
    def initialize(cls) -> None:
        """初始化大纲存储"""
        TemporaryStorage.get_instance('outlines', cls.DEFAULT_TTL)

    @classmethod
    def save_outline(cls, outline: Any, outline_id: Optional[str] = None) -> str:
        """保存大纲

        Args:
            outline: 大纲对象
            outline_id: 可选的大纲ID，如不提供则自动生成

        Returns:
            str: 大纲ID
        """
        storage = TemporaryStorage.get_instance('outlines')

        # 如果未提供ID但对象有id属性，使用对象ID
        if outline_id is None and hasattr(outline, 'id') and outline.id:
            outline_id = outline.id

        # 保存大纲
        return storage.set(outline_id, outline)

    @classmethod
    def get_outline(cls, outline_id: str) -> Optional[Any]:
        """获取大纲

        Args:
            outline_id: 大纲ID

        Returns:
            Optional[Any]: 大纲对象，如不存在则返回None
        """
        storage = TemporaryStorage.get_instance('outlines')
        return storage.get(outline_id)

    @classmethod
    def update_outline(cls, outline_id: str, outline: Any) -> bool:
        """更新大纲

        Args:
            outline_id: 大纲ID
            outline: 新的大纲对象

        Returns:
            bool: 是否成功更新
        """
        storage = TemporaryStorage.get_instance('outlines')
        return storage.update(outline_id, outline)

    @classmethod
    def delete_outline(cls, outline_id: str) -> bool:
        """删除大纲

        Args:
            outline_id: 大纲ID

        Returns:
            bool: 是否成功删除
        """
        storage = TemporaryStorage.get_instance('outlines')
        return storage.delete(outline_id)

    @classmethod
    def list_outlines(cls) -> List[str]:
        """列出所有大纲ID

        Returns:
            List[str]: 大纲ID列表
        """
        storage = TemporaryStorage.get_instance('outlines')
        return storage.list_keys()
