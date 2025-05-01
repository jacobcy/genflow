"""Test ContentType Pydantic Model"""
import pytest
from pydantic import ValidationError

# Model to test
from core.models.content_type.content_type import ContentTypeModel


def test_content_type_model_creation():
    """Test basic creation and field access"""
    data = {
        "name": "博客",
        "depth": "中等",
        "description": "个人观点和分享",
        "word_count": "1200-2000",
        "focus": "观点和案例",
        "style": "个性化",
        "structure": "引言-主体-结论",
        "needs_expert": False,
        "needs_data_analysis": False
    }
    model = ContentTypeModel(**data)
    assert model.name == "博客"
    assert model.depth == "中等"
    assert model.description == "个人观点和分享"
    assert model.word_count == "1200-2000"
    assert model.focus == "观点和案例"
    assert model.style == "个性化"
    assert model.structure == "引言-主体-结论"
    assert not model.needs_expert
    assert not model.needs_data_analysis
    assert model.id == "博客" # Test id property

def test_content_type_model_missing_required_field():
    """Test validation error on missing required field"""
    data = {
        # Missing 'name'
        "depth": "中等",
        "description": "个人观点和分享",
        "word_count": "1200-2000",
        "focus": "观点和案例",
        "style": "个性化",
        "structure": "引言-主体-结论"
    }
    with pytest.raises(ValidationError):
        ContentTypeModel(**data)

def test_content_type_model_get_summary():
    """Test the get_type_summary method"""
    data = {
        "name": "教程",
        "depth": "中等",
        "description": "操作步骤教学",
        "word_count": "1500-3000",
        "focus": "实操性",
        "style": "教学式",
        "structure": "步骤式",
        "needs_expert": True,
        "needs_data_analysis": False
    }
    model = ContentTypeModel(**data)
    summary = model.get_type_summary()

    expected_summary = {
        "name": "教程",
        "description": "操作步骤教学",
        "focus": "实操性",
        "structure": "步骤式",
        "style": "教学式",
        "word_count": "1500-3000",
        "research_needs": {
            "depth": "中等",
            "needs_expert": True,
            "needs_data_analysis": False
        }
    }
    assert summary == expected_summary 