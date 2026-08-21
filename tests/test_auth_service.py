from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.core import Base
from src.services.user_service import UserService
from src.services.auth_service import AuthService
from src.services.schemas import UserCreate, UserLogin
from src.exceptions.user_exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
)

# Test database4 setup
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)


def test_register_user():
    """Test user registration"""

    db = SessionLocal()
    service = UserService(db)

    # Create user data
    user_data = UserCreate(
        email="john@example.com",
        first_name="John",
        last_name="Doe",
        password="Password123",
    )

    # Register user
    user = service.create_user(user_data)

    # Verify registration
    assert user.email == "john@example.com"
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.id is not None

    db.close()


def test_login_user():
    """Test user login"""
    db = SessionLocal()
    service = UserService(db)

    # First, register a user
    user_data = UserCreate(
        email="jane@example.com",
        first_name="Jane",
        last_name="Doe",
        password="Password123",
    )
    registered_user = service.create_user(user_data)

    # Now try to login
    login_data = UserLogin(email="jane@example.com", password="Password123")
    authenticated_user = service.authenticate_user(login_data)

    # Verify login worked
    assert authenticated_user.id == registered_user.id
    assert authenticated_user.email == "jane@example.com"

    db.close()


def test_login_wrong_password():
    """Test login with wrong password"""
    db = SessionLocal()
    service = UserService(db)

    # Register a user
    user_data = UserCreate(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password="CorrectPassword",
    )
    service.create_user(user_data)

    # Try to login with wrong password
    login_data = UserLogin(email="test@example.com", password="WrongPassword")

    try:
        service.authenticate_user(login_data)
        assert False, "Should have raised InvalidCredentialsError"
    except InvalidCredentialsError:
        assert True

    db.close()


def test_register_duplicate_email():
    """Test registering with duplicate email"""
    db = SessionLocal()
    service = UserService(db)

    # Register first user
    user_data = UserCreate(
        email="duplicate@example.com",
        first_name="First",
        last_name="User",
        password="Password123",
    )
    service.create_user(user_data)

    # Try to register with same email
    duplicate_data = UserCreate(
        email="duplicate@example.com",
        first_name="Second",
        last_name="User",
        password="Password456",
    )

    try:
        service.create_user(duplicate_data)
        assert False, "Should have raised UserAlreadyExistsError"
    except UserAlreadyExistsError:
        assert True

    db.close()


def test_jwt_token_creation():
    """Test JWT token creation and verification"""
    # Create token
    user_id = "12345"
    token = AuthService.create_access_token(data={"user_id": user_id})

    # Verify token
    payload = AuthService.verify_access_token(token)

    # Check token contains user_id
    assert payload is not None
    assert payload.get("user_id") == user_id
