from http import HTTPStatus

from fastapi_zero.schemas import UserPublic


def test_create_user(client):
    response = client.post(
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


def test_post_integrity_username_error(client, user):
    response = client.post(
        "/users/",
        json={
            "username": "johndoe",
            "email": "casa@example.com",
            "password": "secret",
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json().get("detail") == "Username já cadastrado"


def test_post_integrity_email_error(client, user):
    response = client.post(
        "/users/",
        json={
            "username": "casa",
            "email": "johndoe@example.com",
            "password": "secret",
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json().get("detail") == "Email já cadastrado"


def test_read_users(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump(
        mode="json"
    )  # foi preciso passar o mode=json para que
    # o python converta o formato do python para json
    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


def test_read_user_by_inexistent_id(client, token):

    response = client.get("users/999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_read_user_by_id_with_user(client, user, token):
    response = client.get("users/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == HTTPStatus.OK
    assert response.json().get("id") == 1


def test_update_user_ok(client, user, token):
    response = client.put(
        "/users/1",
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


def test_update_user_forbidden(client, token):
    response = client.put(
        "/users/999",
        json={
            "username": "non_existent_user",
            "email": "non_existent_user@example.com",
            "password": "no_secret",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_update_integrity_username_error(client, user, token):
    client.post(
        "/users/",
        json={
            "username": "test_update_integrity",
            "email": "test_update_integrity@example.com",
            "password": "no_secret",
        },
    )

    response = client.put(
        "/users/1",
        json={
            "username": "test_update_integrity",
            "email": "johndoe@example.com",
            "password": "secret",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.json().get("detail") == "Username já cadastrado"
    assert response.status_code == HTTPStatus.CONFLICT


def test_update_integrity_email_error(client, user, token):
    client.post(
        "/users/",
        json={
            "username": "test_update",
            "email": "test_update_integrity@example.com",
            "password": "no_secret",
        },
    )

    response = client.put(
        "/users/1",
        json={
            "username": "test_update_integrity",
            "email": "test_update_integrity@example.com",
            "password": "secret",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.json().get("detail") == "Email já cadastrado"
    assert response.status_code == HTTPStatus.CONFLICT


def test_delete_user(client, user, token):
    response = client.delete("/users/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted"}
