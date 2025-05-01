import pytest
from unittest.mock import patch, MagicMock, call
from core.models.db import initialize as db_initialize
from core.models.db.session import get_db # Ensure get_db is importable

# Module to test
import core.models.db.initialize as db_initialize

@patch('core.models.db.initialize.init_database_structure_and_defaults')
@patch('core.models.db.initialize.migrate_all')
def test_initialize_all_calls_steps(mock_migrate_all, mock_init_structure):
    """Test that initialize_all calls structure/defaults init and migration."""
    mock_init_structure.return_value = True
    mock_migrate_all.return_value = True

    result = db_initialize.initialize_all(sync_mode=False)

    assert result is True
    mock_init_structure.assert_called_once()
    mock_migrate_all.assert_called_once_with(sync_mode=False)

@patch('core.models.db.initialize.init_database_structure_and_defaults')
@patch('core.models.db.initialize.migrate_all')
def test_initialize_all_calls_steps_sync_mode(mock_migrate_all, mock_init_structure):
    """Test that initialize_all passes sync_mode correctly."""
    mock_init_structure.return_value = True
    mock_migrate_all.return_value = True

    result = db_initialize.initialize_all(sync_mode=True)

    assert result is True
    mock_init_structure.assert_called_once()
    mock_migrate_all.assert_called_once_with(sync_mode=True)

@patch('core.models.db.initialize.init_database_structure_and_defaults')
@patch('core.models.db.initialize.migrate_all')
def test_initialize_all_handles_structure_failure(mock_migrate_all, mock_init_structure):
    """Test that initialize_all stops if structure/defaults init fails."""
    mock_init_structure.return_value = False # Simulate failure
    mock_migrate_all.return_value = True

    result = db_initialize.initialize_all(sync_mode=False)

    assert result is False
    mock_init_structure.assert_called_once()
    mock_migrate_all.assert_not_called() # Should not be called if first step fails

@patch('core.models.content_type.content_type_db.ensure_default_content_types')
@patch('core.models.db.initialize.migrate_all')
@patch('core.models.db.initialize.init_database_structure')
def test_init_database_structure_and_defaults_calls(
    mock_init_structure, mock_migrate_all, mock_ensure_defaults
):
    """Test that init_database_structure_and_defaults calls necessary steps."""
    mock_init_structure.return_value = True
    mock_migrate_all.return_value = True
    mock_ensure_defaults.return_value = True

    result = db_initialize.init_database_structure_and_defaults(sync_mode=False)

    assert result is True
    mock_init_structure.assert_called_once()
    mock_migrate_all.assert_called_once_with(sync_mode=False)
    mock_ensure_defaults.assert_called_once()

# Correct patch targets based on actual function calls
@patch('core.models.db.initialize.create_tables') # Patches the imported 'create_tables' alias
@patch('core.models.db.initialize.get_db') # Patches the imported 'get_db'
@patch('core.models.content_type.content_type_db.ensure_default_content_types') # Patches the source function
@patch('core.models.db.initialize._ensure_default_style') # Patches internal function
@patch('core.models.db.initialize._ensure_default_platform') # Patches internal function
def test_init_database_structure_and_defaults_calls(
    mock_ensure_platform, mock_ensure_style, mock_ensure_ct, mock_get_db, mock_create_tables
):
    """Test that init_database_structure_and_defaults calls its internal steps."""
    # Setup mocks
    mock_db_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db_session
    mock_ensure_ct.return_value = True # Simulate defaults were added/existed
    mock_ensure_style.return_value = True
    mock_ensure_platform.return_value = True

    # Call the function
    result = db_initialize.init_database_structure_and_defaults()

    # Assertions
    assert result is True
    mock_create_tables.assert_called_once()
    mock_get_db.assert_called_once()
    mock_ensure_ct.assert_called_once_with(mock_db_session)
    mock_ensure_style.assert_called_once_with(mock_db_session)
    mock_ensure_platform.assert_called_once_with(mock_db_session)
    # Check commit was called because defaults were added
    mock_db_session.commit.assert_called_once()

# Add a test case for when defaults already exist (commit not called)
@patch('core.models.db.initialize.create_tables')
@patch('core.models.db.initialize.get_db')
@patch('core.models.content_type.content_type_db.ensure_default_content_types')
@patch('core.models.db.initialize._ensure_default_style')
@patch('core.models.db.initialize._ensure_default_platform')
def test_init_database_structure_defaults_exist(
    mock_ensure_platform, mock_ensure_style, mock_ensure_ct, mock_get_db, mock_create_tables
):
    """Test init_database_structure_and_defaults when defaults exist (no commit)."""
    mock_db_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db_session
    # Simulate defaults already exist
    mock_ensure_ct.return_value = False
    mock_ensure_style.return_value = False
    mock_ensure_platform.return_value = False

    result = db_initialize.init_database_structure_and_defaults()

    assert result is True
    mock_create_tables.assert_called_once()
    mock_get_db.assert_called_once()
    mock_ensure_ct.assert_called_once_with(mock_db_session)
    mock_ensure_style.assert_called_once_with(mock_db_session)
    mock_ensure_platform.assert_called_once_with(mock_db_session)
    # Commit should NOT be called
    mock_db_session.commit.assert_not_called()

# We could add tests for the command-line interface part (__main__ block)
# using subprocess or mocking sys.argv and argparse, but skipping for now
# as we focus on the core capability interface.

# We also skip testing the internal _ensure_default_* helpers directly,
# focusing on the orchestration in init_database_structure_and_defaults. 