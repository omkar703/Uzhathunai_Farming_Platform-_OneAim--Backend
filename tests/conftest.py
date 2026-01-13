"""
Pytest configuration and fixtures for Uzhathunai v2.0 tests.
"""
import pytest
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User, RefreshToken
from app.core.security import get_password_hash

# Test database URL (use actual PostgreSQL database)
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/uzhathunai_db_v2"

# Create test engine
engine = create_engine(TEST_DATABASE_URL)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """
    Create a database session for each test with transaction rollback.
    Uses the actual PostgreSQL database but rolls back changes after each test.
    """
    # Create connection and begin transaction
    connection = engine.connect()
    transaction = connection.begin()
    
    # Create session bound to connection
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        # Rollback transaction to undo all changes
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with database dependency override.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db: Session) -> User:
    """
    Create a test user.
    """
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("TestPass123!"),
        first_name="Test",
        last_name="User",
        phone="+1234567890",
        preferred_language="en",
        is_active=True,
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user_data():
    """
    Test user registration data.
    """
    return {
        "email": "newuser@example.com",
        "password": "NewPass123!",
        "first_name": "New",
        "last_name": "User",
        "phone": "+1234567891",
        "preferred_language": "en"
    }


@pytest.fixture
def auth_headers(client: TestClient, test_user: User) -> dict:
    """
    Get authentication headers for test user.
    """
    # Login to get token
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "TestPass123!",
            "remember_me": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    access_token = data["tokens"]["access_token"]
    
    return {"Authorization": f"Bearer {access_token}"}
