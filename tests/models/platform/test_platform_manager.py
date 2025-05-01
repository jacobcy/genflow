"""Tests for PlatformManager"""
import pytest
import os
from unittest.mock import patch, MagicMock

# Module to test
from core.models.platform.platform_manager import PlatformManager
from core.models.platform.platform import Platform

# Mock data for platforms
MOCK_PLATFORM_DATA_1 = {
    "id": "platform1",
    "name": "Platform One",
    "description": "First test platform",
    # Add other fields as needed by Platform model...
}
MOCK_PLATFORM_DATA_2 = {
    "id": "platform2",
    "name": "Platform Two",
    # ...
}

# Helper to reset manager state between tests
@pytest.fixture(autouse=True)
def reset_manager_state():
    PlatformManager._initialized = False
    PlatformManager._platforms = {}
    yield
    PlatformManager._initialized = False
    PlatformManager._platforms = {}

# --- Test Initialization and Loading --- 

@patch('core.models.platform.platform_manager.os.path.isdir')
@patch('core.models.platform.platform_manager.os.listdir')
@patch('core.models.platform.platform_manager.load_json_config')
def test_initialization_loads_from_collection(mock_load_json, mock_listdir, mock_isdir):
    """Test that initialize loads JSON files from the collection directory."""
    mock_isdir.return_value = True
    mock_listdir.return_value = ["platform1.json", "platform2.json", "not_a_platform.txt"]
    
    # Configure side effect for load_json_config based on filename
    def load_side_effect(file_path):
        if file_path.endswith("platform1.json"):
            return MOCK_PLATFORM_DATA_1
        elif file_path.endswith("platform2.json"):
            return MOCK_PLATFORM_DATA_2
        else:
            return None # Simulate error or non-JSON content
    mock_load_json.side_effect = load_side_effect

    PlatformManager.initialize()

    assert PlatformManager._initialized is True
    assert len(PlatformManager._platforms) == 2 # Only loaded 2 JSONs
    assert "platform1" in PlatformManager._platforms
    assert "platform2" in PlatformManager._platforms
    assert isinstance(PlatformManager._platforms["platform1"], Platform)
    assert PlatformManager._platforms["platform1"].name == "Platform One"
    
    # Check that load_json_config was called for the JSON files
    assert mock_load_json.call_count == 2
    # Check listdir and isdir were called
    mock_listdir.assert_called_once()
    mock_isdir.assert_called_once()

@patch('core.models.platform.platform_manager.os.path.isdir', return_value=False)
def test_initialization_dir_not_found(mock_isdir):
    """Test initialization when the collection directory doesn't exist."""
    PlatformManager.initialize()
    assert PlatformManager._initialized is True # Initialization still completes
    assert len(PlatformManager._platforms) == 0 # But no platforms loaded
    mock_isdir.assert_called_once()

@patch('core.models.platform.platform_manager.os.path.isdir', return_value=True)
@patch('core.models.platform.platform_manager.os.listdir', return_value=["invalid.json"])
@patch('core.models.platform.platform_manager.load_json_config', return_value=None) # Simulate load error
def test_initialization_load_error(mock_load_json, mock_listdir, mock_isdir):
    """Test initialization when JSON loading fails."""
    PlatformManager.initialize()
    assert PlatformManager._initialized is True
    assert len(PlatformManager._platforms) == 0
    mock_load_json.assert_called_once()

@patch('core.models.platform.platform_manager.os.path.isdir', return_value=True)
@patch('core.models.platform.platform_manager.os.listdir', return_value=["no_id.json"])
@patch('core.models.platform.platform_manager.load_json_config')
def test_initialization_missing_id(mock_load_json, mock_listdir, mock_isdir):
    """Test skipping platform data if 'id' field is missing."""
    mock_load_json.return_value = {"name": "No ID Platform"} # Missing 'id'
    PlatformManager.initialize()
    assert PlatformManager._initialized is True
    assert len(PlatformManager._platforms) == 0
    mock_load_json.assert_called_once()


# --- Test Accessor Methods --- (Assume manager is initialized by mocks) ---

# Use parametrize to run getter tests with pre-loaded mock data
@pytest.mark.parametrize("platform_id, expected_name", [
    ("platform1", "Platform One"),
    ("platform2", "Platform Two"),
    ("nonexistent", None)
])
@patch('core.models.platform.platform_manager.PlatformManager._load_platforms') # Prevent actual loading
def test_get_platform(mock_load, platform_id, expected_name):
    """Test get_platform method."""
    # Manually set the cache for the test
    PlatformManager._platforms = {
        "platform1": Platform(**MOCK_PLATFORM_DATA_1),
        "platform2": Platform(**MOCK_PLATFORM_DATA_2)
    }
    PlatformManager._initialized = True # Mark as initialized

    platform = PlatformManager.get_platform(platform_id)
    if expected_name:
        assert isinstance(platform, Platform)
        assert platform.name == expected_name
    else:
        assert platform is None
    assert mock_load.call_count == 0 # Ensure _load_platforms wasn't called

@pytest.mark.parametrize("search_name, expected_id", [
    ("Platform One", "platform1"),
    ("platform one", "platform1"), # Case-insensitive
    ("Platform Two", "platform2"),
    ("Platform Three", None)
])
@patch('core.models.platform.platform_manager.PlatformManager._load_platforms')
def test_get_platform_by_name(mock_load, search_name, expected_id):
    """Test get_platform_by_name method."""
    PlatformManager._platforms = {
        "platform1": Platform(**MOCK_PLATFORM_DATA_1),
        "platform2": Platform(**MOCK_PLATFORM_DATA_2)
    }
    PlatformManager._initialized = True

    platform = PlatformManager.get_platform_by_name(search_name)
    if expected_id:
        assert isinstance(platform, Platform)
        assert platform.id == expected_id
    else:
        assert platform is None

@patch('core.models.platform.platform_manager.PlatformManager._load_platforms')
def test_get_all_platforms(mock_load):
    """Test get_all_platforms method."""
    PlatformManager._platforms = {
        "platform1": Platform(**MOCK_PLATFORM_DATA_1),
        "platform2": Platform(**MOCK_PLATFORM_DATA_2)
    }
    PlatformManager._initialized = True

    all_platforms = PlatformManager.get_all_platforms()
    assert isinstance(all_platforms, list)
    assert len(all_platforms) == 2
    ids = {p.id for p in all_platforms}
    assert ids == {"platform1", "platform2"} 