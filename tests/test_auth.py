from http import HTTPStatus

import pytest
from freezegun import freeze_time
from jwt import encode


@pytest.mark.asyncio
async def test_get_token(client, user):
    response = await client.post(
        "/auth/token", data={"username": user.email, "password": user.clean_password}
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token["token_type"] == "Bearer"
    assert "access_token" in token


@pytest.mark.asyncio
async def test_jwt_invalid_token(client):
    response = await client.delete(
        "/users/1", headers={"Authorization": "Bearer token-invalido"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}


@pytest.mark.asyncio
async def test_get_current_user_without_sub(client, settings):
    token = encode({}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    response = await client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_email_non_existent(client, settings):
    token = encode(
        {"sub": "abcd@1234.com"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    response = await client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_token_expired_after_time(client, user):
    with freeze_time("2026-03-23 12:00:00"):
        response = await client.post(
            "/auth/token",
            data={"username": user.email, "password": user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()["access_token"]

    with freeze_time("2026-03-23 12:31:00"):
        response = await client.put(
            f"/users/{user.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "wrongwrong",
                "email": "wrong@wrong.com",
                "password": "wrong",
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate credentials"}


@pytest.mark.asyncio
async def test_token_inexistent_user(client):
    response = await client.post(
        "/auth/token",
        data={"username": "no_user@no_domain.com", "password": "testtest"},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect email or password"}


@pytest.mark.asyncio
async def test_token_wrong_password(client, user):
    response = await client.post(
        "/auth/token", data={"username": user.email, "password": "wrong_password"}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect email or password"}


@pytest.mark.asyncio
async def test_refresh_token(client, user, token):
    response = await client.post(
        "/auth/refresh_token",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_token_expired_dont_refresh(client, user):
    with freeze_time("2026-03-23 12:00:00"):
        response = await client.post(
            "/auth/token",
            data={"username": user.email, "password": user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()["access_token"]

    with freeze_time("2026-03-23 12:31:00"):
        response = await client.post(
            "/auth/refresh_token",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate credentials"}
