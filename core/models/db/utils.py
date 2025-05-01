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
