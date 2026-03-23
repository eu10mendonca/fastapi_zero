import pytest
from sqlalchemy import select

from fastapi_zero.models import User
from fastapi_zero.schemas import UserDB


# Teste com artifício para mockar o created_at, usando o event do SQLAlchemy
@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(
        model=User, event_name="before_insert", fields=("created_at", "updated_at")
    ) as mock_time:
        new_user = User(
            username="testuser", password="testpass", email="test@example.com"
        )
        session.add(new_user)
        await session.commit()

    new_user = await session.scalar(select(User).where(User.username == "testuser"))

    user_schema = UserDB.model_validate(new_user)
    assert user_schema.model_dump() == {
        "id": 1,
        "username": "testuser",
        "password": "testpass",
        "email": "test@example.com",
        "created_at": mock_time,
        "updated_at": mock_time,
    }


@pytest.mark.asyncio
async def test_update_user(session, mock_db_time):
    new_user = User(username="testuser", password="testpass", email="test@example.com")
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    with mock_db_time(
        model=User, event_name="before_update", fields=("updated_at",)
    ) as mock_updated_time:
        new_user.password = "testpass2"
        await session.commit()
        await session.refresh(new_user)

    user_schema = UserDB.model_validate(new_user)
    assert user_schema.model_dump() == {
        "id": 1,
        "username": "testuser",
        "password": "testpass2",
        "email": "test@example.com",
        "created_at": new_user.created_at,
        "updated_at": mock_updated_time,
    }
