from httpx import AsyncClient


async def test_pytest(client: AsyncClient):
    assert True
