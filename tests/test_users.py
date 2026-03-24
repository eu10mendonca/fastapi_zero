from http import HTTPStatus

import pytest

from fastapi_zero.schemas import UserPublic


@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post(
        "/users/",
        json={
            "username": "johndoe",
            "email": "johndoe@example.com",
            "password": "secret",
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "username": "johndoe",
        "email": "johndoe@example.com",
        "id": 1,
        "created_at": response.json()["created_at"],
        "updated_at": response.json()["updated_at"],
    }


@pytest.mark.asyncio
async def test_post_integrity_username_error(client, user):
    response = await client.post(
        "/users/",
        json={
            "username": user.username,
            "email": "casa@example.com",
            "password": "secret",
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json().get("detail") == "Username já cadastrado"


@pytest.mark.asyncio
async def test_post_integrity_email_error(client, user):
    response = await client.post(
        "/users/",
        json={
            "username": "casa",
            "email": user.email,
            "password": "secret",
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json().get("detail") == "Email já cadastrado"


@pytest.mark.asyncio
async def test_read_users(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump(
        mode="json"
    )  # foi preciso passar o mode=json para que
    # o python converta o formato do python para json
    response = await client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


@pytest.mark.asyncio
async def test_read_user_by_inexistent_id(client, token):
    response = await client.get(
        "users/999", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_read_user_by_id_with_user(client, user, token):
    response = await client.get("users/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == HTTPStatus.OK
    assert response.json().get("id") == 1


@pytest.mark.asyncio
async def test_update_user_ok(client, user, token):
    response = await client.put(
        f"/users/{user.id}",
        json={
            "username": "john_doe_updated",
            "email": "john_doe_updated@example.com",
            "password": "new_secret",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": 1,
        "username": "john_doe_updated",
        "email": "john_doe_updated@example.com",
        "created_at": response.json().get("created_at"),
        "updated_at": response.json().get("updated_at"),
    }


@pytest.mark.asyncio
async def test_update_integrity_username_error(client, user, token, other_user):

    response = await client.put(
        f"/users/{user.id}",
        json={
            "username": other_user.username,
            "email": "johndoe@example.com",
            "password": "secret",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.json().get("detail") == "Username já cadastrado"
    assert response.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_update_integrity_email_error(client, user, token, other_user):

    response = await client.put(
        f"/users/{user.id}",
        json={
            "username": "test_update_integrity",
            "email": other_user.email,
            "password": "secret",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.json().get("detail") == "Email já cadastrado"
    assert response.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_update_user_with_wrong_user(client, other_user, token):
    response = await client.put(
        f"/users/{other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "mynewpassword",
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permissions"}


@pytest.mark.asyncio
async def test_delete_user_wrong_user(client, other_user, token):
    response = await client.delete(
        f"/users/{other_user.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permissions"}


@pytest.mark.asyncio
async def test_delete_user(client, user, token):
    response = await client.delete(
        "/users/1", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted"}
