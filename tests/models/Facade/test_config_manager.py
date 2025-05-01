import pytest
from unittest.mock import patch, MagicMock, call

# Import the class to test
from core.models.facade.config_manager import ConfigManager

# Import dependent managers and models for type hints and potentially mock return values
from core.models.style.style_manager import StyleManager
from core.models.content_type.content_type_manager import ContentTypeManager
from core.models.platform.platform_manager import PlatformManager
from core.models.style.article_style import ArticleStyle # Example model

@pytest.fixture(autouse=True)
def reset_config_manager_singleton():
    """Ensures ConfigManager is reset between tests."""
    ConfigManager._initialized = False
    # Reset any other relevant class variables if needed
    yield
    ConfigManager._initialized = False

# Use patch to mock the dependent managers during tests
@patch('core.models.config_manager.StyleManager', autospec=True)
@patch('core.models.config_manager.ContentTypeManager', autospec=True)
@patch('core.models.config_manager.PlatformManager', autospec=True)
def test_config_manager_initialization(MockPlatformManager, MockContentTypeManager, MockStyleManager):
    """Test that ConfigManager initializes all underlying managers."""
    ConfigManager.initialize(use_db=True)

    MockStyleManager.initialize.assert_called_once_with(use_db=True)
    MockContentTypeManager.initialize.assert_called_once_with() # No use_db arg currently
    MockPlatformManager.initialize.assert_called_once_with()   # No use_db arg currently
    assert ConfigManager._initialized is True

    # Test idempotency (calling initialize again does nothing)
    MockStyleManager.initialize.reset_mock()
    MockContentTypeManager.initialize.reset_mock()
    MockPlatformManager.initialize.reset_mock()
    ConfigManager.initialize(use_db=True)
    MockStyleManager.initialize.assert_not_called()
    MockContentTypeManager.initialize.assert_not_called()
    MockPlatformManager.initialize.assert_not_called()


@patch('core.models.config_manager.StyleManager', autospec=True)
@patch('core.models.config_manager.ContentTypeManager', autospec=True)
@patch('core.models.config_manager.PlatformManager', autospec=True)
def test_config_manager_delegates_to_style_manager(MockPlatformManager, MockContentTypeManager, MockStyleManager):
    """Test that ConfigManager correctly delegates style methods to StyleManager."""
    # Ensure manager is initialized before testing delegation
    ConfigManager.initialize(use_db=False)
    assert ConfigManager._initialized is True # Pre-check

    # --- Test Style Methods Delegation ---
    style_name = "formal"
    style_type = "professional"
    description = "A test style description"
    options = {"some_option": True}
    mock_style = MagicMock(spec=ArticleStyle)
    mock_style.name = style_name

    # get_article_style
    MockStyleManager.get_article_style.return_value = mock_style
    ret_style = ConfigManager.get_article_style(style_name)
    MockStyleManager.get_article_style.assert_called_once_with(style_name)
    assert ret_style == mock_style

    # get_default_style
    MockStyleManager.get_default_style.return_value = mock_style
    ret_default = ConfigManager.get_default_style()
    MockStyleManager.get_default_style.assert_called_once_with()
    assert ret_default == mock_style

    # get_all_styles
    all_styles_dict = {style_name: mock_style}
    MockStyleManager.get_all_styles.return_value = all_styles_dict
    ret_all = ConfigManager.get_all_styles()
    MockStyleManager.get_all_styles.assert_called_once_with()
    assert ret_all == all_styles_dict

    # create_style_from_description - REMOVED because StyleManager doesn't have this method
    # MockStyleManager.create_style_from_description.return_value = mock_style
    # ret_created = ConfigManager.create_style_from_description(description, options)
    # MockStyleManager.create_style_from_description.assert_called_once_with(description, options)
    # assert ret_created == mock_style

    # find_style_by_type
    MockStyleManager.find_style_by_type.return_value = mock_style
    ret_found = ConfigManager.find_style_by_type(style_type)
    MockStyleManager.find_style_by_type.assert_called_once_with(style_type)
    assert ret_found == mock_style

    # save_style
    MockStyleManager.save_style.return_value = True
    ret_saved = ConfigManager.save_style(mock_style)
    MockStyleManager.save_style.assert_called_once_with(mock_style)
    assert ret_saved is True

    # --- Test Ensure Initialized Check ---
    # Reset initialized flag and mocks
    ConfigManager._initialized = False
    MockStyleManager.initialize.reset_mock()
    MockContentTypeManager.initialize.reset_mock()
    MockPlatformManager.initialize.reset_mock()
    MockStyleManager.get_article_style.reset_mock()


    # Call a method without initializing first
    ConfigManager.get_article_style("any_style")

    # Verify initialize was called implicitly
    MockStyleManager.initialize.assert_called_once()
    MockContentTypeManager.initialize.assert_called_once()
    MockPlatformManager.initialize.assert_called_once()
    # Verify the actual method was called *after* initialization
    MockStyleManager.get_article_style.assert_called_once_with("any_style")
    assert ConfigManager._initialized is True # Should be set by ensure_initialized

# Add similar delegation tests for ContentTypeManager and PlatformManager methods later
# e.g., test_config_manager_delegates_to_content_type_manager
# e.g., test_config_manager_delegates_to_platform_manager
