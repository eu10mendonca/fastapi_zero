import pytest


@pytest.mark.asyncio
async def test_read_root(client):
    response = await client.get("/")

    assert response.json()["message"] == "Hello World!"
