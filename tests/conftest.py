import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from core.database import Base, get_db

# Import models so Base.metadata knows about them
import models.cart
import models.order

from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function", autouse=True)
def wipe_database():
    # If using sqlite in-memory, session-level create_all + dropping data would be cleaner,
    # but for simplicity recreate tables per function to isolate tests properly 
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    
@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c

@pytest.fixture
def user_headers():
    return {
        "x-user-id": "1",
        "x-user-role": "customer"
    }

@pytest.fixture
def venue_headers():
    return {
        "x-user-id": "2",
        "x-user-role": "venue",
        "x-user-venue-id": "venue_user"
    }
