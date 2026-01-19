from http import HTTPStatus


def test_root_deve_retornar_hello_world(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello World!'}


def test_get_hello_world_deve_retornar_html_com_hello_world(client):
    response = client.get('/hello-world')
    assert response.status_code == HTTPStatus.OK
    assert '<!DOCTYPE html>' in response.text or '<html>' in response.text
    assert '<h1>Hello World!</h1>' in response.text


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'johndoe',
        'email': 'johndoe@example.com',
        'id': 1,
    }


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'username': 'johndoe',
                'email': 'johndoe@example.com',
            }
        ]
    }


def test_update_user_ok(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'john_doe_updated',
            'email': 'john_doe_updated@example.com',
            'password': 'new_secret',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'john_doe_updated',
        'email': 'john_doe_updated@example.com',
    }


def test_update_user_not_found(client):
    response = client.put(
        '/users/999',
        json={
            'username': 'non_existent_user',
            'email': 'non_existent_user@example.com',
            'password': 'no_secret',
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_not_found(client):
    response = client.delete('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
