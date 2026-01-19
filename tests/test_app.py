from http import HTTPStatus

from fastapi.testclient import TestClient

from fastapi_zero.app import app


def test_root_deve_retornar_hello_world():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Hello World!"}


def test_get_hello_world_deve_retornar_html_com_hello_world():
    client = TestClient(app)
    response = client.get("/hello-world")
    assert response.status_code == HTTPStatus.OK
    assert "<!DOCTYPE html>" in response.text or "<html>" in response.text
    assert "<h1>Hello World!</h1>" in response.text
