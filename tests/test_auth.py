from http import HTTPStatus

import pytest
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
