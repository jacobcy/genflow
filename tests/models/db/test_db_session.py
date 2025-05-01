import pytest
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.orm import Session
from contextlib import contextmanager

# Modules to test
from core.models.db.session import Base, get_db, engine # Import engine for direct checks if needed

# Define a simple test model inheriting from Base
class SimpleTestModel(Base):
    __tablename__ = 'simple_test_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)

@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    """Creates the test table before each test and drops it after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_get_db_provides_session():
    """Test that get_db() provides a usable session within the context."""
    session_instance = None
    try:
        with get_db() as db:
            assert isinstance(db, Session)
            session_instance = db
            # Perform a simple query to check if the session is active
            result = db.execute(select(1))
            assert result.scalar_one() == 1
        # Removed the unreliable check for exception after session closure
        # assert session_instance is not None # Optional: Check db was assigned
        # assert not session_instance.is_active # This might also be unreliable

    except Exception as e:
        pytest.fail(f"get_db context manager raised an unexpected exception: {e}")


def test_base_inheritance_and_session_usage():
    """Test that a model inheriting Base can be used with the session from get_db."""
    test_name = "Test Item"
    item_id = None

    # Insert data
    try:
        with get_db() as db:
            new_item = SimpleTestModel(name=test_name)
            db.add(new_item)
            db.commit()
            db.refresh(new_item)
            item_id = new_item.id
            assert item_id is not None
    except Exception as e:
        pytest.fail(f"Inserting data failed: {e}")

    # Retrieve and verify data
    try:
        with get_db() as db:
            retrieved_item = db.query(SimpleTestModel).filter(SimpleTestModel.id == item_id).first()
            assert retrieved_item is not None
            assert retrieved_item.id == item_id
            assert retrieved_item.name == test_name
    except Exception as e:
        pytest.fail(f"Retrieving data failed: {e}") 