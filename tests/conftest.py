import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db, make_engine
from app.main import app
from app.models import Base


@pytest.fixture
def db_session():
    # Fresh in-memory database per test; StaticPool keeps the single connection alive.
    engine = make_engine("sqlite://", poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)
    with TestSession() as session:
        yield session


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    # No `with` block: the app's startup (which creates tables in the real DB) doesn't run.
    yield TestClient(app)
    app.dependency_overrides.clear()


def register_and_login(client: TestClient, email: str, password: str = "secret123") -> dict:
    """Creates a user and returns the Authorization header for them."""
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    r = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def auth_headers(client):
    return register_and_login(client, "ahmed@example.com")
