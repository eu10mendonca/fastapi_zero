from contextlib import contextmanager
from datetime import datetime, timezone

import factory
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fastapi_zero.app import app
from fastapi_zero.base import Base
from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.security import get_password_hash
from fastapi_zero.settings import Settings

# @pytest.fixture
# def client():
#     return TestClient(app)


class UserFactory(factory.Factory):  # type: ignore
    class Meta:  # type: ignore
        model = User

    username = factory.Sequence(lambda n: f"test{n}")  # type: ignore
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@test.com")  # type: ignore
    password = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")  # type: ignore


@pytest_asyncio.fixture
async def client(session):
    async def get_session_override():
        yield session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="htpp://test") as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_zero_test",
        echo=True,
    )
    # Base.metadata.create_all(engine)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # with Session(engine) as session:
    #     yield session

    # Base.metadata.drop_all(engine)


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


@pytest_asyncio.fixture
async def user(session):
    password = "secret"
    user = UserFactory(password=get_password_hash(password))
    # user = User(
    #     username="johndoe",
    #     email="johndoe@example.com",
    #     password=get_password_hash(password),
    # )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Adicionado em tempo de execução apenas para poder validar a criptografia da senha.
    user.clean_password = password  # type: ignore

    return user


@pytest_asyncio.fixture
async def other_user(session):
    password = "secret"
    user = UserFactory(password=get_password_hash(password))
    # user = User(
    #     username="johndoe",
    #     email="johndoe@example.com",
    #     password=get_password_hash(password),
    # )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Adicionado em tempo de execução apenas para poder validar a criptografia da senha.
    user.clean_password = password  # type: ignore

    return user


@pytest_asyncio.fixture
async def token(client, user):
    response = await client.post(
        "/auth/token", data={"username": user.email, "password": user.clean_password}
    )
    return response.json()["access_token"]


@pytest.fixture
def settings():
    return Settings()  # type:ignore
