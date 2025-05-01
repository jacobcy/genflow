"""Test ContentTypeName SQLAlchemy model and related functions."""
import pytest
from datetime import datetime, timezone # Import timezone

# Database session and model
from core.models.db.session import get_db, Base, engine
from core.models.content_type.content_type_db import (
    ContentTypeName,
    ensure_default_content_types,
    DEFAULT_CONTENT_TYPES
)

# Fixture to setup/teardown the database table for tests in this file
@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    """Creates the table before each test and drops it after."""
    # Ensure the specific table for ContentTypeName is created
    ContentTypeName.__table__.create(bind=engine, checkfirst=True)
    yield
    # Drop the table after the test
    ContentTypeName.__table__.drop(bind=engine, checkfirst=True)

def test_content_type_name_creation_and_retrieval():
    """Test creating and retrieving a ContentTypeName instance."""
    test_name = "测试类型"
    created_at_before = datetime.now(timezone.utc)
    instance_id = None

    with get_db() as db:
        instance = ContentTypeName(name=test_name)
        db.add(instance)
        db.commit()
        # Re-fetch the instance to ensure we get the value from the DB
        # This also helps confirm the commit worked.
        db.expire(instance) # Expire the instance to force reload from DB on next access
        instance = db.query(ContentTypeName).filter(ContentTypeName.name == test_name).first()
        assert instance is not None # Ensure refetch worked

        instance_id = instance.name # Primary key is name

        # Make the retrieved datetime timezone-aware (assuming UTC)
        retrieved_created_at = instance.created_at
        assert retrieved_created_at is not None # Check it was set
        if retrieved_created_at.tzinfo is None:
            retrieved_created_at = retrieved_created_at.replace(tzinfo=timezone.utc)

        # Now compare two aware datetimes
        assert retrieved_created_at >= created_at_before

    assert instance_id == test_name

    # Retrieve and verify
    with get_db() as db:
        retrieved = db.query(ContentTypeName).filter(ContentTypeName.name == test_name).first()
        assert retrieved is not None
        assert retrieved.name == test_name
        assert retrieved.created_at is not None
        assert retrieved.__repr__() == f"<ContentTypeName {test_name}>"
        # Check to_dict method
        retrieved_dict = retrieved.to_dict()
        assert retrieved_dict["name"] == test_name
        assert isinstance(retrieved_dict["created_at"], str) # Should be ISO format string
        retrieved_dt = datetime.fromisoformat(retrieved_dict["created_at"].replace('Z', '+00:00'))
        assert (datetime.now(timezone.utc) - retrieved_dt).total_seconds() < 5 # Check within 5 seconds

def test_ensure_default_content_types():
    """Test that ensure_default_content_types adds missing default types."""
    # 1. Run ensure_default_content_types on an empty table
    with get_db() as db:
        ensure_default_content_types(db) # Call the function to test

    # Verify all default types were added
    with get_db() as db:
        count = db.query(ContentTypeName).count()
        assert count == len(DEFAULT_CONTENT_TYPES)
        for type_name in DEFAULT_CONTENT_TYPES:
            assert db.query(ContentTypeName).filter(ContentTypeName.name == type_name).first() is not None

    # 2. Run ensure_default_content_types again, should be idempotent
    first_run_timestamps = {}
    with get_db() as db:
        for type_name in DEFAULT_CONTENT_TYPES:
             instance = db.query(ContentTypeName).filter(ContentTypeName.name == type_name).first()
             first_run_timestamps[type_name] = instance.created_at

    with get_db() as db:
        ensure_default_content_types(db) # Call again

    # Verify count is still the same and timestamps haven't changed (or changed minimally)
    with get_db() as db:
        count = db.query(ContentTypeName).count()
        assert count == len(DEFAULT_CONTENT_TYPES)
        for type_name in DEFAULT_CONTENT_TYPES:
             instance = db.query(ContentTypeName).filter(ContentTypeName.name == type_name).first()
             assert instance.created_at == first_run_timestamps[type_name] # Check timestamp didn't change

def test_ensure_default_content_types_partial_existing():
    """Test ensure_default_content_types when some defaults already exist."""
    # Add one of the default types manually first
    existing_type_name = DEFAULT_CONTENT_TYPES[0]
    with get_db() as db:
        db.add(ContentTypeName(name=existing_type_name))
        db.commit()

    # Run ensure_default_content_types
    with get_db() as db:
        ensure_default_content_types(db)

    # Verify all default types exist now
    with get_db() as db:
        count = db.query(ContentTypeName).count()
        assert count == len(DEFAULT_CONTENT_TYPES)
        for type_name in DEFAULT_CONTENT_TYPES:
            assert db.query(ContentTypeName).filter(ContentTypeName.name == type_name).first() is not None 