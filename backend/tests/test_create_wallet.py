import pytest
from test_services.manager import WalletManager
from tests.utils.assertions import assert_wallet


@pytest.fixture
async def wallet_manager(client):
    return WalletManager(client)


async def test_create_wallet(wallet_manager):
    """Позитив проверка создания кошелька"""

    response = await wallet_manager.post_wallets(json={})
    response_json = response.json()

    assert response.status_code == 201
    assert_wallet(response_json)
    assert response_json["balance"] == 0.0
