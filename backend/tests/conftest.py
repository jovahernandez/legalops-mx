"""Test fixtures using SQLite in-memory for fast tests."""

import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Tenant, User
from app.dependencies import hash_password, create_access_token

SQLALCHEMY_TEST_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def seed_tenant(db):
    tenant = Tenant(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        name="Test Tenant",
        settings_json={},
    )
    db.add(tenant)
    db.commit()
    return tenant


@pytest.fixture
def seed_user(db, seed_tenant):
    user = User(
        id=uuid.UUID("00000000-0000-0000-0000-000000000010"),
        tenant_id=seed_tenant.id,
        email="test@test.com",
        hashed_password=hash_password("test123"),
        full_name="Test User",
        role="admin",
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def auth_headers(seed_user):
    token = create_access_token({"sub": str(seed_user.id), "tenant_id": str(seed_user.tenant_id), "role": seed_user.role})
    return {"Authorization": f"Bearer {token}"}
