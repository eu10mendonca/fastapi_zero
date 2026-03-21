from http import HTTPStatus

from jwt import encode


def test_login_for_access_token(client, user):
    response = client.post(
        "/auth/token", data={"username": user.email, "password": user.clean_password}
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token["token_type"] == "Bearer"
    assert "access_token" in token


def test_jwt_invalid_token(client):
    response = client.delete(
        "/users/1", headers={"Authorization": "Bearer token-invalido"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}


def test_get_current_user_without_sub(client, settings):
    token = encode({}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_get_current_user_email_non_existent(client, settings):
    token = encode(
        {"sub": "abcd@1234.com"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.UNAUTHORIZED
