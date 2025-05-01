"""Tests for the Platform Pydantic model."""
import pytest
from pydantic import ValidationError

# Models to test
from core.models.platform.platform import Platform, PlatformConstraints, TechnicalRequirements


def test_platform_creation_minimal():
    """Test creating a Platform with minimal required fields."""
    data = {"id": "test_platform", "name": "Test Platform"}
    platform = Platform(**data)
    assert platform.id == "test_platform"
    assert platform.name == "Test Platform"
    assert platform.description == ""
    assert platform.category == "general"
    assert platform.primary_language == "zh-CN"
    assert platform.supported_languages == ["zh-CN"]
    assert isinstance(platform.constraints, PlatformConstraints)
    assert isinstance(platform.technical, TechnicalRequirements)
    assert platform.manual_review_likely is True

def test_platform_creation_full():
    """Test creating a Platform with all fields populated."""
    data = {
        "id": "full_platform",
        "name": "Full Platform",
        "url": "https://full.com",
        "description": "A full example",
        "category": "testing",
        "primary_language": "en-US",
        "supported_languages": ["en-US", "fr-FR"],
        "constraints": {
            "min_length": 10,
            "max_length": 5000,
            "max_title_length": 50,
            "max_image_count": 5,
            "max_video_count": 1,
            "forbidden_words": ["spam", "test"],
            "required_elements": ["footer"],
            "allowed_formats": ["markdown"],
            "allowed_media_types": ["image/jpeg"],
            "code_block_support": False,
            "math_formula_support": True,
            "table_support": False,
            "emoji_support": False
        },
        "technical": {
            "api_endpoint": "https://api.full.com/v2",
            "api_version": "v2",
            "max_request_size_kb": 10240,
            "supported_media_upload_formats": ["image/jpeg"],
            "auth_method": "APIKey",
            "https_required": True
        },
        "manual_review_likely": False
    }
    platform = Platform(**data)
    assert platform.id == "full_platform"
    assert platform.name == "Full Platform"
    assert platform.url == "https://full.com"
    assert platform.category == "testing"
    assert platform.constraints.min_length == 10
    assert platform.constraints.forbidden_words == ["spam", "test"]
    assert platform.technical.api_version == "v2"
    assert platform.manual_review_likely is False

def test_platform_missing_required_id():
    """Test ValidationError when required 'id' field is missing."""
    data = {"name": "Platform Without ID"}
    with pytest.raises(ValidationError):
        Platform(**data)

def test_platform_missing_required_name():
    """Test ValidationError when required 'name' field is missing."""
    data = {"id": "platform_without_name"}
    with pytest.raises(ValidationError):
        Platform(**data)

def test_nested_model_defaults():
    """Test that nested models get their default values."""
    data = {"id": "nested_defaults", "name": "Nested Defaults"}
    platform = Platform(**data)
    # Check some defaults from PlatformConstraints
    assert platform.constraints.min_length == 0
    assert platform.constraints.max_image_count == 20
    assert platform.constraints.forbidden_words == []
    assert platform.constraints.allowed_formats == ["text"]
    # Check some defaults from TechnicalRequirements
    assert platform.technical.api_endpoint is None
    assert platform.technical.max_request_size_kb == 5120
    assert platform.technical.https_required is True 