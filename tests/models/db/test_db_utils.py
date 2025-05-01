import pytest
import json
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Modules to test
from core.models.db.utils import JSONEncodedDict
from core.models.db.session import Base # Need Base to define the model

# Setup in-memory SQLite database for testing
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define a test model using JSONEncodedDict
class JsonTestModel(Base):
    __tablename__ = 'json_test_table'
    id = Column(Integer, primary_key=True)
    data = Column(JSONEncodedDict) # Use the custom type
    name = Column(String) # Add another column for variety

@pytest.fixture(scope="function")
def db_session():
    """Provides a database session for a test function."""
    Base.metadata.create_all(bind=engine) # Create table
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine) # Drop table

def test_json_encoded_dict_storage_retrieval(db_session: Session):
    """Test storing and retrieving dictionary via JSONEncodedDict."""
    test_data = {"key1": "value1", "nested": {"num": 123, "bool": True}}
    item_name = "json_item"

    # Create and store item
    new_item = JsonTestModel(name=item_name, data=test_data)
    db_session.add(new_item)
    db_session.commit()
    item_id = new_item.id
    assert item_id is not None

    # Clear session cache (optional but good practice)
    db_session.expire_all()

    # Retrieve item
    retrieved_item = db_session.query(JsonTestModel).filter(JsonTestModel.id == item_id).first()

    assert retrieved_item is not None
    assert retrieved_item.name == item_name
    # Check if the retrieved data matches the original dictionary
    assert retrieved_item.data == test_data
    assert retrieved_item.data["key1"] == "value1"
    assert retrieved_item.data["nested"]["num"] == 123

def test_json_encoded_dict_handles_none(db_session: Session):
    """Test storing and retrieving None via JSONEncodedDict."""
    item_name = "none_item"

    # Create and store item with None data
    new_item = JsonTestModel(name=item_name, data=None)
    db_session.add(new_item)
    db_session.commit()
    item_id = new_item.id
    assert item_id is not None

    db_session.expire_all()

    # Retrieve item
    retrieved_item = db_session.query(JsonTestModel).filter(JsonTestModel.id == item_id).first()

    assert retrieved_item is not None
    assert retrieved_item.name == item_name
    assert retrieved_item.data is None

def test_json_encoded_dict_handles_empty_dict(db_session: Session):
    """Test storing and retrieving an empty dictionary."""
    item_name = "empty_dict_item"
    test_data = {}

    new_item = JsonTestModel(name=item_name, data=test_data)
    db_session.add(new_item)
    db_session.commit()
    item_id = new_item.id

    db_session.expire_all()
    retrieved_item = db_session.query(JsonTestModel).filter(JsonTestModel.id == item_id).first()

    assert retrieved_item is not None
    assert retrieved_item.data == {} 