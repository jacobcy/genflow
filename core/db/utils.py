import time
from typing import Dict, Any, TypeVar, Type
from sqlalchemy.types import TypeDecorator, TEXT
import json
T = TypeVar('T')

class JSONEncodedDict(TypeDecorator):
    """存储和检索JSON格式的字典"""
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value, ensure_ascii=False)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class TopicAdapter:
    """话题模型适配器，处理不同类型话题模型之间的转换"""

    @staticmethod
    def orm_to_pydantic(orm_topic) -> Any:
        """ORM模型转Pydantic模型"""
        from core.models.topic import Topic
        data = orm_topic.to_dict()
        # 移除Pydantic不需要的字段
        data.pop('created_at', None)
        data.pop('updated_at', None)
        return Topic(**data)

    @staticmethod
    def pydantic_to_orm(pydantic_topic) -> Any:
        """Pydantic模型转ORM模型"""
        from core.db import  Topic
        return Topic(**pydantic_topic.to_dict())

    @staticmethod
    def handle_time_fields(data: Dict[str, Any]) -> Dict[str, Any]:
        """处理时间字段兼容性"""
        data_copy = data.copy()
        current_time = int(time.time())

        # 处理source_time字段
        if 'source_time' not in data_copy:
            # 优先使用fetch_time，其次使用timestamp
            data_copy['source_time'] = data_copy.get('fetch_time',
                                data_copy.get('timestamp', current_time))

        # 处理expire_time字段
        if 'expire_time' not in data_copy:
            # 默认7天后过期
            data_copy['expire_time'] = current_time + 7 * 24 * 60 * 60

        return data_copy
