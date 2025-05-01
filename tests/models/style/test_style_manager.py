# tests/models/style/test_style_manager.py

import pytest
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Assuming StyleManager is importable and ArticleStyle exists
from core.models.style.style_manager import StyleManager
from core.models.style.article_style import ArticleStyle

# Dummy valid style data
STYLE_DEFAULT = {
    "name": "default", "type": "general", "description": "Default style",
    "tone": "Neutral", "formality": 3, "content_types": ["blog", "generic"],
    "target_audience": "General", "emotion": False, "emoji": False,
    "language_level": "Intermediate", "recommended_patterns": [], "examples": []
}
STYLE_FORMAL = {
    "name": "formal", "type": "professional", "description": "Formal style",
    "tone": "Formal", "formality": 5, "content_types": ["report"],
    "target_audience": "Professionals", "emotion": False, "emoji": False,
    "language_level": "Advanced", "recommended_patterns": ["Precise language"], "examples": []
}
STYLE_BILIBILI = { # Example for find_by_type test
    "name": "bilibili", "type": "entertainment", "description": "Bilibili style",
    "tone": "Energetic", "formality": 2, "content_types": ["video_script"],
    "target_audience": "Young audience", "emotion": True, "emoji": True,
    "language_level": "Intermediate", "recommended_patterns": ["Use memes"], "examples": []
}

# Store original config dir path at module level
_ORIGINAL_STYLE_CONFIG_DIR = StyleManager.CONFIG_DIR

@pytest.fixture(scope="function")
def temp_style_collection(tmp_path: Path) -> Path:
    """Creates a temporary collection directory with dummy style JSON files."""
    collection_dir = tmp_path / "style_collection"
    collection_dir.mkdir()

    # Valid files
    (collection_dir / "default.json").write_text(json.dumps(STYLE_DEFAULT))
    (collection_dir / "formal.json").write_text(json.dumps(STYLE_FORMAL))
    (collection_dir / "bilibili.json").write_text(json.dumps(STYLE_BILIBILI))


    # Invalid JSON
    (collection_dir / "invalid.json").write_text("{invalid json")

    # Non-JSON file
    (collection_dir / "notes.txt").write_text("This is not JSON.")

    # JSON with missing required field (name)
    invalid_data = STYLE_FORMAL.copy()
    del invalid_data["name"]
    (collection_dir / "missing_name.json").write_text(json.dumps(invalid_data))


    return collection_dir

# Use a single fixture to manage StyleManager state for tests
@pytest.fixture(autouse=True)
def manage_style_manager_state(temp_style_collection):
    """Resets StyleManager state and temporarily points CONFIG_DIR to temp dir."""
    # Reset state before test
    StyleManager._initialized = False
    StyleManager._configs = {}
    StyleManager.CONFIG_DIR = temp_style_collection # Point to temp dir for the test
    yield # Run the test
    # Reset state after test
    StyleManager._initialized = False
    StyleManager._configs = {}
    StyleManager.CONFIG_DIR = _ORIGINAL_STYLE_CONFIG_DIR # Restore original path


# Remove the patch decorator for CONFIG_DIR from tests below
# The manage_style_manager_state fixture now handles this

# @patch('core.models.style.style_manager.StyleManager.CONFIG_DIR', new_callable=MagicMock)
def test_style_manager_initialization(): # Remove mock_config_dir and temp_style_collection args
    """Test StyleManager loads valid configs on initialization."""
    # mock_config_dir.__str__.return_value = str(temp_style_collection) # No longer needed

    # Initialize (use_db=False as we don't test DB interaction here)
    StyleManager.initialize(use_db=False)

    assert StyleManager._initialized is True
    assert "default" in StyleManager._configs
    assert "formal" in StyleManager._configs
    assert "bilibili" in StyleManager._configs
    assert len(StyleManager._configs) == 3 # Only valid ones loaded

    # Check if loaded data matches
    assert StyleManager._configs["default"].name == "default"
    assert StyleManager._configs["formal"].formality == 5
    assert isinstance(StyleManager._configs["default"], ArticleStyle)

    # Ensure invalid ones were skipped (check logs if logger is configured, or lack of key)
    assert "invalid" not in StyleManager._configs
    assert "notes" not in StyleManager._configs
    assert "missing_name" not in StyleManager._configs

# @patch('core.models.style.style_manager.StyleManager.CONFIG_DIR', new_callable=MagicMock)
def test_get_article_style(): # Remove mock_config_dir and temp_style_collection args
    """Test retrieving specific styles."""
    # mock_config_dir.__str__.return_value = str(temp_style_collection) # No longer needed
    StyleManager.initialize(use_db=False)

    formal_style = StyleManager.get_article_style("formal")
    assert formal_style is not None
    assert formal_style.name == "formal"
    assert formal_style.type == "professional"

    non_existent_style = StyleManager.get_article_style("non_existent")
    assert non_existent_style is None

# @patch('core.models.style.style_manager.StyleManager.CONFIG_DIR', new_callable=MagicMock)
def test_get_default_style(): # Remove mock_config_dir and temp_style_collection args
    """Test retrieving the default style."""
    # mock_config_dir.__str__.return_value = str(temp_style_collection) # No longer needed
    StyleManager.initialize(use_db=False)

    default_style = StyleManager.get_default_style()
    assert default_style is not None
    assert default_style.name == "default"
    assert default_style.type == "general"

# @patch('core.models.style.style_manager.StyleManager.CONFIG_DIR', new_callable=MagicMock)
def test_get_all_styles(): # Remove mock_config_dir and temp_style_collection args
    """Test retrieving all loaded styles."""
    # mock_config_dir.__str__.return_value = str(temp_style_collection) # No longer needed
    StyleManager.initialize(use_db=False)

    all_styles = StyleManager.get_all_styles()
    assert isinstance(all_styles, dict)
    assert len(all_styles) == 3
    assert "default" in all_styles
    assert "formal" in all_styles
    assert "bilibili" in all_styles
    assert isinstance(all_styles["default"], ArticleStyle)

# @patch('core.models.style.style_manager.StyleManager.CONFIG_DIR', new_callable=MagicMock)
def test_find_style_by_type(): # Remove mock_config_dir and temp_style_collection args
    """Test finding a style by its type."""
    # mock_config_dir.__str__.return_value = str(temp_style_collection) # No longer needed
    StyleManager.initialize(use_db=False)

    entertainment_style = StyleManager.find_style_by_type("entertainment")
    assert entertainment_style is not None
    assert entertainment_style.name == "bilibili"

    professional_style = StyleManager.find_style_by_type("professional")
    assert professional_style is not None
    assert professional_style.name == "formal"

    non_existent_type = StyleManager.find_style_by_type("non_existent_type")
    assert non_existent_type is None

# Test save_style (requires writing to the temp directory)
# We skip mocking the DB part by using use_db=False in initialize
# @patch('core.models.style.style_manager.StyleManager.CONFIG_DIR', new_callable=MagicMock) # Remove patch
def test_save_style(temp_style_collection: Path): # Add temp_style_collection argument back
    """Test saving a new style to the collection."""
    # mock_config_dir.__str__.return_value = str(temp_style_collection) # No longer needed
    StyleManager.initialize(use_db=False) # Initialize first

    new_style_data = {
        "name": "casual_blog", "type": "blogging", "description": "Casual blog style",
        "tone": "Conversational", "formality": 2, "content_types": ["blog"],
        "target_audience": "General readers", "emotion": True, "emoji": True,
        "language_level": "Intermediate", "recommended_patterns": [], "examples": []
    }
    new_style = ArticleStyle(**new_style_data)

    # Ensure it doesn't exist first
    assert StyleManager.get_article_style("casual_blog") is None
    assert len(StyleManager.get_all_styles()) == 3

    # Save the style
    success = StyleManager.save_style(new_style)
    assert success is True


    # Verify file was created in the temp directory
    saved_file_path = temp_style_collection / "casual_blog.json"
    assert saved_file_path.exists()

    # Verify file content
    with open(saved_file_path, 'r') as f:
        saved_data = json.load(f)
        assert saved_data["name"] == "casual_blog"
        assert saved_data["tone"] == "Conversational"

    # Verify internal state updated
    assert StyleManager.get_article_style("casual_blog") is not None
    assert StyleManager.get_article_style("casual_blog").type == "blogging"
    assert len(StyleManager.get_all_styles()) == 4

    # Test saving an existing style (update)
    updated_style_data = new_style_data.copy()
    updated_style_data["tone"] = "Witty"
    updated_style = ArticleStyle(**updated_style_data)

    success_update = StyleManager.save_style(updated_style)
    assert success_update is True
    assert StyleManager.get_article_style("casual_blog").tone == "Witty"
    assert len(StyleManager.get_all_styles()) == 4 # Count shouldn't increase

# Note: Testing `create_style_from_description` is complex if it involves external calls (LLM).
# If it's just internal logic, it can be tested. If it relies on external services,
# those should be mocked. Assuming it's primarily a placeholder or simple constructor for now.
# We will test the ConfigManager delegation instead. 