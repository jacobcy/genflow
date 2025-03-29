"""独立模型测试

测试独立的数据模型，不依赖外部导入
"""
import pytest
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


# 定义用于测试的独立模型
class TestConfig(BaseModel):
    """测试配置模型"""
    name: str = Field(..., description="配置名称")
    value: Any = Field(..., description="配置值")
    description: Optional[str] = Field(default=None, description="配置描述")
    is_active: bool = Field(default=True, description="是否激活")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    tags: List[str] = Field(default_factory=list, description="配置标签")

    def activate(self) -> bool:
        """激活配置"""
        self.is_active = True
        return True

    def deactivate(self) -> bool:
        """停用配置"""
        self.is_active = False
        return True


# 测试基本模型创建和属性
def test_model_creation():
    """测试模型创建"""
    config = TestConfig(
        name="test_config",
        value={"key": "value"},
        description="测试配置"
    )

    assert config.name == "test_config"
    assert config.value == {"key": "value"}
    assert config.description == "测试配置"
    assert config.is_active is True
    assert isinstance(config.created_at, datetime)
    assert isinstance(config.tags, list)
    assert len(config.tags) == 0


# 测试模型方法
def test_model_methods():
    """测试模型方法"""
    config = TestConfig(
        name="test_config",
        value=42
    )

    # 测试停用方法
    assert config.is_active is True
    config.deactivate()
    assert config.is_active is False

    # 测试激活方法
    config.activate()
    assert config.is_active is True


# 测试模型序列化
def test_model_serialization():
    """测试模型序列化"""
    config = TestConfig(
        name="test_config",
        value={"numbers": [1, 2, 3]},
        tags=["test", "config"]
    )

    # 转换为字典
    config_dict = config.model_dump()

    assert isinstance(config_dict, dict)
    assert config_dict["name"] == "test_config"
    assert config_dict["value"] == {"numbers": [1, 2, 3]}
    assert config_dict["is_active"] is True
    assert "created_at" in config_dict
    assert config_dict["tags"] == ["test", "config"]


# 测试模型验证
def test_model_validation():
    """测试模型验证"""
    # 测试必填字段缺失情况
    with pytest.raises(Exception):
        # 缺少必填字段name和value
        TestConfig()  # type: ignore

    with pytest.raises(Exception):
        # 缺少必填字段value
        TestConfig(name="missing_value")  # type: ignore

    # 测试字段类型不匹配情况
    with pytest.raises(Exception):
        # name字段类型不匹配
        TestConfig(name=123, value="test")  # type: ignore

    # 有效数据应该正常创建
    config = TestConfig(name="valid", value=None)
    assert config.name == "valid"
    assert config.value is None
