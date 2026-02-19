from sqlalchemy import select

from fastapi_zero.models import User
from fastapi_zero.schemas import UserDB

# Teste sen validar o created_at, pois ele é gerado automaticamente no banco de dados
# def test_create_user(session):
#     user = User(username='testuser', password='testpass', email='test@example.com')

#     session.add(user)
#     session.commit()

#     # Para garantir que o objeto user seja atualizado com o
#     # inserido gerado no banco de dados, precisamos
#     # usar session.refresh(user) após o commit.
#     # session.refresh(user)
#     # Ou pegar o usuário através de um select
#     user = session.scalar(select(User).where(User.username == 'testuser'))

#     # As validações podem ser realizadas dessa forma,
#     # ou usando o model_validate doo pydantic
#     # assert user.id is not None
#     # print(f"Id do usuário: {user.id}")
#     # # breakpoint() # Use this to inspect the user object in the test
#     # assert user.username == "testuser"
#     # assert user.password == "testpass"
#     # assert user.email == "test@example.com"
#     # print(f"Usuário criado em: {user.created_at}")
#     # assert user.created_at is not None

#     user_schema = UserDB.model_validate(user)

#     assert user_schema.model_dump() == {
#         'id': 1,
#         'username': 'testuser',
#         'password': 'testpass',
#         'email': 'test@example.com',
#         # "created_at": user.created_at,
#     }


# Teste com artifício para mockar o created_at, usando o event do SQLAlchemy
def test_create_user(session, mock_db_time):
    with mock_db_time(
        model=User, event_name="before_insert", fields=("created_at", "updated_at")
    ) as mock_time:
        new_user = User(
            username="testuser", password="testpass", email="test@example.com"
        )
        session.add(new_user)
        session.commit()
        new_user = session.scalar(select(User).where(User.username == "testuser"))

    user_schema = UserDB.model_validate(new_user)
    assert user_schema.model_dump() == {
        "id": 1,
        "username": "testuser",
        "password": "testpass",
        "email": "test@example.com",
        "created_at": mock_time,
        "updated_at": mock_time,
    }


def test_update_user(session, mock_db_time):

    new_user = User(username="testuser", password="testpass", email="test@example.com")
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    with mock_db_time(
        model=User, event_name="before_update", fields=("updated_at",)
    ) as mock_updated_time:
        new_user.password = "testpass2"
        session.commit()
        session.refresh(new_user)

    user_schema = UserDB.model_validate(new_user)
    assert user_schema.model_dump() == {
        "id": 1,
        "username": "testuser",
        "password": "testpass2",
        "email": "test@example.com",
        "created_at": new_user.created_at,
        "updated_at": mock_updated_time,
    }
