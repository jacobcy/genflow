"""Tests for the PlatformDB SQLAlchemy model."""
import pytest
from datetime import datetime, timezone

# Database session and model
from core.models.db.session import get_db, Base, engine
from core.models.platform.platform_db import PlatformDB

# Fixture to setup/teardown the database table
@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    """Creates the table before each test and drops it after."""
    PlatformDB.__table__.create(bind=engine, checkfirst=True)
    yield
    PlatformDB.__table__.drop(bind=engine, checkfirst=True)

def test_platform_db_creation_and_retrieval():
    """Test creating and retrieving a PlatformDB instance."""
    platform_id = "test-db-platform"
    platform_name = "Test DB Platform"
    now = datetime.now(timezone.utc)
    mock_constraints = {"min_length": 10, "max_image_count": 5}
    mock_technical = {"api_endpoint": "https://api.test.com"}

    with get_db() as db:
        instance = PlatformDB(
            id=platform_id,
            name=platform_name,
            description="DB test description",
            is_enabled=True,
            platform_type="testing",
            url="https://db-test.com",
            constraints=mock_constraints,
            technical=mock_technical
            # created_at and updated_at have defaults
        )
        db.add(instance)
        db.commit()
        # Re-fetch to ensure data is from DB
        db.expire(instance)
        instance = db.query(PlatformDB).filter(PlatformDB.id == platform_id).first()
        assert instance is not None

        assert instance.id == platform_id
        assert instance.name == platform_name
        assert instance.description == "DB test description"
        assert instance.is_enabled is True
        assert instance.platform_type == "testing"
        assert instance.url == "https://db-test.com"
        assert instance.constraints == mock_constraints
        assert instance.technical == mock_technical

        # Make retrieved datetime timezone-aware (assuming UTC) before comparison
        retrieved_created_at = instance.created_at
        assert retrieved_created_at is not None
        if retrieved_created_at.tzinfo is None:
            retrieved_created_at = retrieved_created_at.replace(tzinfo=timezone.utc)

        retrieved_updated_at = instance.updated_at
        assert retrieved_updated_at is not None
        if retrieved_updated_at.tzinfo is None:
            retrieved_updated_at = retrieved_updated_at.replace(tzinfo=timezone.utc)
        
        # Now compare aware datetimes
        assert retrieved_created_at >= now
        assert retrieved_updated_at >= now

        assert repr(instance) == f"<PlatformDB {platform_id}>"

def test_platform_db_update_timestamp():
    """Test that the updated_at timestamp is updated."""
    platform_id = "update-ts-test"
    platform_name = "Update TS Platform"
    initial_time = None

    # Create initial record
    with get_db() as db:
        instance = PlatformDB(id=platform_id, name=platform_name)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        initial_time = instance.updated_at
        assert initial_time is not None

    # Wait briefly to ensure timestamp changes
    # Note: Depending on DB time resolution, this might still be flaky
    # A more robust test might involve mocking time.
    import time
    time.sleep(0.01)

    # Update the record
    with get_db() as db:
        instance_to_update = db.query(PlatformDB).filter(PlatformDB.id == platform_id).first()
        assert instance_to_update is not None
        instance_to_update.description = "Updated description"
        db.commit()
        db.refresh(instance_to_update)
        updated_time = instance_to_update.updated_at

    assert updated_time is not None
    assert updated_time > initial_time

def test_platform_db_to_dict():
    """Test the to_dict method."""
    platform_id = "dict-test"
    platform_name = "Dict Test Platform"
    mock_constraints = {"max_length": 1000}
    
    with get_db() as db:
        instance = PlatformDB(id=platform_id, name=platform_name, constraints=mock_constraints)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        instance_dict = instance.to_dict()

    assert instance_dict["id"] == platform_id
    assert instance_dict["name"] == platform_name
    assert instance_dict["constraints"] == mock_constraints
    assert instance_dict["technical"] is None # Was not set
    assert isinstance(instance_dict["created_at"], str)
    assert isinstance(instance_dict["updated_at"], str) 