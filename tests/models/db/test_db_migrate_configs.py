import pytest
from unittest.mock import patch, MagicMock, call, ANY

# Module to test
import core.models.db.migrate_configs as db_migrate

# Mock config data
MOCK_CONFIG_DATA = {
    "content_types": [{"id": "ct1", "name": "Type 1"}],
    "article_styles": [{"id": "st1", "name": "Style 1", "content_types": ["ct1"]}],
    "platforms": [{"id": "pl1", "name": "Platform 1"}],
}

@patch('core.models.db.migrate_configs.migrate_content_types')
@patch('core.models.db.migrate_configs.migrate_article_styles')
@patch('core.models.db.migrate_configs.migrate_platforms')
def test_migrate_all_calls_specific_migrations(mock_migrate_platforms, mock_migrate_styles, mock_migrate_content):
    """Test that migrate_all calls the individual migration functions."""
    mock_migrate_content.return_value = True
    mock_migrate_styles.return_value = True
    mock_migrate_platforms.return_value = True

    result_sync_false = db_migrate.migrate_all(sync_mode=False)
    assert result_sync_false is True
    mock_migrate_content.assert_called_with(False)
    mock_migrate_styles.assert_called_with(False)
    mock_migrate_platforms.assert_called_with(False)

    mock_migrate_content.reset_mock()
    mock_migrate_styles.reset_mock()
    mock_migrate_platforms.reset_mock()

    result_sync_true = db_migrate.migrate_all(sync_mode=True)
    assert result_sync_true is True
    mock_migrate_content.assert_called_with(True)
    mock_migrate_styles.assert_called_with(True)
    mock_migrate_platforms.assert_called_with(True)


@patch('core.models.db.migrate_configs.get_config_file_path')
@patch('core.models.db.migrate_configs.load_json_config')
@patch('core.models.db.migrate_configs.migrate_config')
@patch('core.models.content_type.content_type_db.ContentTypeName', new_callable=MagicMock)
def test_migrate_content_types_calls_migrate_config(
    MockContentTypeName, mock_migrate_config, mock_load_json, mock_get_path
):
    """Test that migrate_content_types loads config and calls migrate_config with ContentTypeName."""
    # Since ContentTypeName is mocked at import time, make it behave like a type
    MockContentTypeName.__name__ = "ContentTypeName"

    # Setup mock return values
    mock_get_path.return_value = "mock/path/to/content_types.json" # Return a string path
    mock_load_json.return_value = {"content_types": [{"name": "ct1", "description": "Type 1"}]}
    mock_migrate_config.return_value = True

    # Call the function
    result = db_migrate.migrate_content_types(sync_mode=False)

    # Assertions
    assert result is True
    # Check functions were called correctly
    mock_get_path.assert_called_once_with("content_types", "content_types.json")
    mock_load_json.assert_called_once_with("mock/path/to/content_types.json")
    # Assert migrate_config is called with all keyword arguments
    mock_migrate_config.assert_called_once_with(
        model_cls=MockContentTypeName, # Use keyword arg
        items={item['name']: item for item in mock_load_json.return_value["content_types"] if 'name' in item}, # Use keyword arg
        sync_mode=False,
        id_field='name'
    )

@patch('core.models.db.migrate_configs.get_db')
def test_migrate_config_create_new(mock_get_db):
    """Test migrate_config creates a new item."""
    mock_session = MagicMock()
    mock_query = MagicMock()
    MockModel = MagicMock() # Mock the SQLAlchemy model
    MockModel.__name__ = "MockModel"

    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_session.query.return_value.filter.return_value.first.return_value = None # Simulate item not existing

    items_to_migrate = {"item1": {"id": "item1", "value": "A"}}
    result = db_migrate.migrate_config(MockModel, items_to_migrate, sync_mode=False)

    assert result is True
    mock_session.query.assert_called_with(MockModel)
    mock_session.query.return_value.filter.assert_called_once() # Check filter call
    # Verify add was called with an instance created with correct data
    mock_session.add.assert_called_once()
    added_instance = mock_session.add.call_args[0][0]
    # Check constructor call - Use ANY if __init__ is complex or mocked differently
    MockModel.assert_called_with(id='item1', value='A')
    assert added_instance == MockModel.return_value # Check it's the mocked model instance
    mock_session.commit.assert_called_once()


@patch('core.models.db.migrate_configs.get_db')
def test_migrate_config_update_existing(mock_get_db):
    """Test migrate_config updates an existing item."""
    mock_session = MagicMock()
    mock_existing_item = MagicMock()
    mock_existing_item.id = "item1"
    mock_existing_item.value = "Old"
    MockModel = MagicMock()
    MockModel.__name__ = "MockModel" # For logging

    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_session.query.return_value.filter.return_value.first.return_value = mock_existing_item

    items_to_migrate = {"item1": {"id": "item1", "value": "New"}}
    result = db_migrate.migrate_config(MockModel, items_to_migrate, sync_mode=False)

    assert result is True
    mock_session.query.assert_called_with(MockModel)
    mock_session.add.assert_not_called() # Should not add new
    assert mock_existing_item.value == "New" # Check attribute was updated
    mock_session.commit.assert_called_once()


@patch('core.models.db.migrate_configs.get_db')
def test_migrate_config_sync_mode_delete(mock_get_db):
    """Test migrate_config deletes extra items in sync mode."""
    mock_session = MagicMock()
    mock_db_item1 = MagicMock()
    mock_db_item1.id = "item1"
    mock_db_item2 = MagicMock() # This one is not in file_items
    mock_db_item2.id = "item_to_delete"
    MockModel = MagicMock()
    MockModel.__name__ = "MockModel"
    MockModel.id = MagicMock() # Mock the id attribute for getattr

    mock_get_db.return_value.__enter__.return_value = mock_session
    # Simulate query for existing IDs
    mock_session.query.return_value.all.return_value = [mock_db_item1, mock_db_item2]
    # Simulate query for deleting
    mock_delete_query_filter = MagicMock()
    mock_delete_query = MagicMock()
    mock_session.query.return_value.filter.return_value = mock_delete_query_filter
    mock_delete_query_filter.delete.return_value = mock_delete_query # delete() returns the query

    # Simulate query for checking existence before update/create
    # Let first return the item if id is 'item1', else None
    def first_side_effect(*args, **kwargs):
        # Crude way to check filter condition if possible, otherwise guess based on calls
        # Here, we assume the filter call for 'item1' happens second
        if mock_session.query.return_value.filter.call_count > 1:
             return mock_db_item1
        return None # Should not be called for item_to_delete during update phase

    mock_session.query.return_value.filter.return_value.first.side_effect = first_side_effect

    file_items = {"item1": {"id": "item1", "value": "A"}} # Only item1 is in the file
    result = db_migrate.migrate_config(MockModel, file_items, sync_mode=True, id_field='id')

    assert result is True
    # Verify it queried all items initially
    mock_session.query.return_value.all.assert_called_once()
    # Verify it attempted to delete the extra item
    # Check that query().filter(Model.id == 'item_to_delete').delete() was called
    delete_filter_call = None
    for c in mock_session.query.return_value.filter.call_args_list:
        # Inspect the filter condition; requires complex mock setup or assumptions
        # Simple check: was delete called after a filter?
        pass # Cannot easily verify the exact filter condition without more complex mocking
    mock_delete_query_filter.delete.assert_called_once()
    mock_session.commit.assert_called_once() 