from contextlib import contextmanager
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from fastapi_zero.app import app
from fastapi_zero.base import Base
from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.security import get_password_hash
from fastapi_zero.settings import Settings

# @pytest.fixture
# def client():
#     return TestClient(app)


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_zero_test",
        echo=True,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(engine)


@contextmanager
def _mock_db_time(*, model, event_name, time=None, fields):
    if time is None:
        time = datetime.now(timezone.utc)

    def fake_time_hook(mapper, connection, target):
        for field in fields:
            if hasattr(target, field):
                setattr(target, field, time)

    event.listen(model, event_name, fake_time_hook)
    try:
        yield time
    finally:
        event.remove(model, event_name, fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def user(session):
    password = "secret"
    user = User(
        username="johndoe",
        email="johndoe@example.com",
        password=get_password_hash(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Adicionado em tempo de execução apenas para poder validar a criptografia da senha.
    user.clean_password = password  # type: ignore

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        "/auth/token", data={"username": user.email, "password": user.clean_password}
    )
    return response.json()["access_token"]


@pytest.fixture
def settings():
    return Settings()  # type:ignore
