import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.core import Base, get_db  # Import your get_db dependency
from src.main import app

# 1. Setup in-memory SQLite engine with StaticPool (keeps DB alive across connections)
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 2. Pytest fixture to handle DB table creation/cleanup and app overrides per test
@pytest.fixture(name="client")
def client_fixture():
    # Create tables in the in-memory database
    Base.metadata.create_all(bind=engine)

    # Dependency override for get_db
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Yield client to the test
    with TestClient(app) as client:
        yield client

    # Cleanup tables and reset overrides after each test run
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


# -------------------------------------------------------------------
# TESTS
# -------------------------------------------------------------------


def test_register_and_login(client):
    """Test registering and logging in via HTTP"""
    register_response = client.post(
        "/auth/register",
        json={
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "TestPassword123",
        },
    )
    assert register_response.status_code == 201
    assert register_response.json()["email"] == "testuser@example.com"

    login_response = client.post(
        "/auth/login",
        json={"email": "testuser@example.com", "password": "TestPassword123"},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_create_todo_with_auth(client):
    """Test creating a todo with authentication"""
    client.post(
        "/auth/register",
        json={
            "email": "todotester@example.com",
            "first_name": "Todo",
            "last_name": "Tester",
            "password": "TodoPass123",
        },
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "todotester@example.com", "password": "TodoPass123"},
    )
    token = login_response.json()["access_token"]

    todo_response = client.post(
        "/todos/",
        json={
            "title": "API Test Todo",
            "description": "Testing via HTTP",
            "priority": "high",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert todo_response.status_code == 201
    assert todo_response.json()["title"] == "API Test Todo"
    assert todo_response.json()["completed"] is False


def test_get_todos_with_auth(client):
    """Test getting todos with authentication"""
    client.post(
        "/auth/register",
        json={
            "email": "gettodos@example.com",
            "first_name": "Get",
            "last_name": "Todos",
            "password": "GetPass123",
        },
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "gettodos@example.com", "password": "GetPass123"},
    )
    token = login_response.json()["access_token"]

    # Create two todos
    client.post(
        "/todos/",
        json={"title": "Todo 1", "description": "First todo", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/todos/",
        json={"title": "Todo 2", "description": "Second todo", "priority": "low"},
        headers={"Authorization": f"Bearer {token}"},
    )

    get_response = client.get("/todos/", headers={"Authorization": f"Bearer {token}"})

    assert get_response.status_code == 200
    todos = get_response.json()
    assert len(todos) == 2
    assert todos[0]["title"] == "Todo 1"
    assert todos[1]["title"] == "Todo 2"


def test_get_todos_without_auth(client):
    """Test getting todos without authentication (should fail)"""
    response = client.get("/todos/")
    assert response.status_code == 401


def test_create_todo_without_auth(client):
    """Test creating todo without authentication (should fail)"""
    response = client.post(
        "/todos/",
        json={
            "title": "Unauthorized Todo",
            "description": "Should fail",
            "priority": "high",
        },
    )
    assert response.status_code == 401


def test_complete_todo(client):
    """Test marking a todo as complete"""
    client.post(
        "/auth/register",
        json={
            "email": "completetodo@example.com",
            "first_name": "Complete",
            "last_name": "Todo",
            "password": "CompletePass123",
        },
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "completetodo@example.com", "password": "CompletePass123"},
    )
    token = login_response.json()["access_token"]

    create_response = client.post(
        "/todos/",
        json={
            "title": "Todo to Complete",
            "description": "Will complete",
            "priority": "high",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    todo_id = create_response.json()["id"]

    complete_response = client.put(
        f"/todos/{todo_id}/complete", headers={"Authorization": f"Bearer {token}"}
    )

    assert complete_response.status_code == 200
    assert complete_response.json()["completed"] is True


def test_delete_todo(client):
    """Test deleting a todo"""
    client.post(
        "/auth/register",
        json={
            "email": "deletetodo@example.com",
            "first_name": "Delete",
            "last_name": "Todo",
            "password": "DeletePass123",
        },
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "deletetodo@example.com", "password": "DeletePass123"},
    )
    token = login_response.json()["access_token"]

    create_response = client.post(
        "/todos/",
        json={
            "title": "Todo to Delete",
            "description": "Will delete",
            "priority": "high",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    todo_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/todos/{todo_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert delete_response.status_code == 204
