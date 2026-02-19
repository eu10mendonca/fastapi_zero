from contextlib import contextmanager
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from fastapi_zero.app import app
from fastapi_zero.models import Base


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def session():
    # engine = create_engine("sqlite:///:memory:", echo=True)
    engine = create_engine(
        "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_zero", echo=True
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
    # connection = engine.connect()
    # yield connection
    # connection.close()

    Base.metadata.drop_all(engine)


@contextmanager
def _mock_db_time(*, model, event_name, time=None, fields):
    if time is None:
        time = datetime.now(timezone.utc)

    def fake_time_hook(mapper, connection, target):
        for field in fields:
            if hasattr(target, field):
                setattr(target, field, time)

    event.listen(model, event_name, fake_time_hook)
    try:
        yield time
    finally:
        event.remove(model, event_name, fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time
