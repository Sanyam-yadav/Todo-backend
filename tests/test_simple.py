from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.core import Base
from src.services.todo_service import TodoService
from uuid import uuid4
from src.exceptions.todo_exceptions import TodoNotFoundError

# Create a test database (in memory, not on disk)
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(bind=engine)


def test_create_todo():
    """Test creating a todo"""

    db = SessionLocal()
    service = TodoService(db)

    user_id = uuid4()

    todo = service.create_todo(
        user_id=user_id,
        title="Test Todo",
        description="Testing",
        priority="high",
    )

    assert todo.title == "Test Todo"
    assert todo.description == "Testing"
    assert todo.priority == "high"
    assert todo.completed is False
    assert todo.user_id == user_id

    db.close()


def test_get_todo_by_id():
    """Test getting a todo by ID"""

    db = SessionLocal()
    todo_service = TodoService(db)
    user_id = uuid4()

    todo = todo_service.create_todo(
        user_id=user_id,
        title="Get Me",
        description="Find this",
        priority="high",
    )

    retrieved_todo = todo_service.get_todo_by_id(user_id, todo.id)

    assert retrieved_todo.id == todo.id
    assert retrieved_todo.title == todo.title

    db.close()


def test_get_todo_not_found():
    """Test getting a todo that doesn't exist"""

    db = SessionLocal()
    service = TodoService(db)

    user_id = uuid4()
    fake_todo_id = uuid4()

    try:
        service.get_todo_by_id(user_id, fake_todo_id)
        assert False, "Should have raised TodoNotFoundError"
    except TodoNotFoundError:
        assert True

    db.close()
