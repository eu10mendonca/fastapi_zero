from jwt import decode

from fastapi_zero.security import create_access_token
from fastapi_zero.settings import Settings

settings = Settings()  # type:ignore


def test_jwt(settings):
    data = {"sub": "test"}

    token = create_access_token(data)

    decoded = decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)

    assert decoded["sub"] == data["sub"]
    assert "exp" in decoded
