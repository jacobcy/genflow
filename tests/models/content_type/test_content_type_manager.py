"""Test ContentTypeManager"""
import pytest
from unittest.mock import patch, MagicMock

# Module to test
from core.models.content_type.content_type_manager import ContentTypeManager
from core.models.content_type.content_type import ContentTypeModel
from core.models.content_type.constants import (
    RESEARCH_CONFIG, WRITING_CONFIG, CATEGORY_TO_CONTENT_TYPE,
    CONTENT_TYPE_BLOG, CONTENT_TYPE_TECH # Import some known types
)

def test_manager_initialization():
    """Test that the manager initializes and loads data."""
    # Explicitly initialize for this test
    ContentTypeManager.initialize()
    assert ContentTypeManager._initialized is True
    assert len(ContentTypeManager._content_types) == len(RESEARCH_CONFIG)
    # Check if a known type was loaded correctly
    blog_type = ContentTypeManager._content_types.get(CONTENT_TYPE_BLOG)
    assert isinstance(blog_type, ContentTypeModel)
    assert blog_type.name == CONTENT_TYPE_BLOG
    # Verify some merged data (example)
    assert blog_type.word_count == WRITING_CONFIG[CONTENT_TYPE_BLOG]["word_count"]
    # Reset state after test to avoid interference if not using fixture
    ContentTypeManager._initialized = False
    ContentTypeManager._content_types = {}

def test_get_content_type():
    """Test getting a specific content type."""
    ContentTypeManager.initialize() # Explicitly initialize
    blog_type = ContentTypeManager.get_content_type(CONTENT_TYPE_BLOG)
    assert isinstance(blog_type, ContentTypeModel)
    assert blog_type.name == CONTENT_TYPE_BLOG

    non_existent = ContentTypeManager.get_content_type("不存在的类型")
    assert non_existent is None
    ContentTypeManager._initialized = False
    ContentTypeManager._content_types = {}

def test_get_all_content_types():
    """Test getting all content types."""
    ContentTypeManager.initialize() # Explicitly initialize
    all_types = ContentTypeManager.get_all_content_types()
    assert isinstance(all_types, dict)
    assert len(all_types) == len(RESEARCH_CONFIG)
    assert CONTENT_TYPE_BLOG in all_types
    assert isinstance(all_types[CONTENT_TYPE_BLOG], ContentTypeModel)
    # Ensure it's a copy
    all_types["new_key"] = "test"
    assert "new_key" not in ContentTypeManager._content_types
    ContentTypeManager._initialized = False
    ContentTypeManager._content_types = {}

def test_get_content_type_by_category():
    """Test getting content type by category mapping."""
    ContentTypeManager.initialize() # Explicitly initialize
    # Test a known mapping
    tech_category = "技术" # Assuming this maps to CONTENT_TYPE_TECH
    expected_type_name = CATEGORY_TO_CONTENT_TYPE.get(tech_category)
    assert expected_type_name == CONTENT_TYPE_TECH # Verify assumption

    tech_type = ContentTypeManager.get_content_type_by_category(tech_category)
    assert isinstance(tech_type, ContentTypeModel)
    assert tech_type.name == CONTENT_TYPE_TECH

    # Test an unknown category
    unknown_type = ContentTypeManager.get_content_type_by_category("未知分类")
    assert unknown_type is None

    # Test a category that maps to a type not in RESEARCH_CONFIG (edge case)
    test_cat = "test_cat_maps_to_nothing"
    CATEGORY_TO_CONTENT_TYPE[test_cat] = "类型不存在于配置中"
    # Ensure manager is re-initialized if needed after modifying constants? Or assume it picks up?
    # Let's assume the test runs fast enough or constants are read live.
    assert ContentTypeManager.get_content_type_by_category(test_cat) is None
    del CATEGORY_TO_CONTENT_TYPE[test_cat] # Clean up test modification
    ContentTypeManager._initialized = False
    ContentTypeManager._content_types = {}

def test_get_default_content_type():
    """Test getting the default content type."""
    ContentTypeManager.initialize() # Explicitly initialize
    default_type = ContentTypeManager.get_default_content_type()
    assert isinstance(default_type, ContentTypeModel)
    assert default_type.name == CONTENT_TYPE_BLOG # Default is currently BLOG
    ContentTypeManager._initialized = False
    ContentTypeManager._content_types = {}

# Test that initialization is idempotent
def test_initialization_idempotent():
    """Test that calling initialize multiple times is safe."""
    # Reset state before this specific test
    ContentTypeManager._initialized = False
    ContentTypeManager._content_types = {}

    # Patch the loading logic to count calls
    with patch.object(ContentTypeManager, '_load_content_types', wraps=ContentTypeManager._load_content_types) as mock_load:
        # First call
        ContentTypeManager.initialize()
        assert mock_load.call_count == 1 # Should be called once
        assert ContentTypeManager._initialized is True
        call_count_before = mock_load.call_count

        # Second call
        ContentTypeManager.initialize()
        assert mock_load.call_count == call_count_before # Should not call load again

        # Call via ensure_initialized
        ContentTypeManager.ensure_initialized()
        assert mock_load.call_count == call_count_before # Should also not call load again

    # Reset state after test
    ContentTypeManager._initialized = False
    ContentTypeManager._content_types = {} 