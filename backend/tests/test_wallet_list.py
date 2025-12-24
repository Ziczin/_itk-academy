import pytest
from test_services.manager import WalletManager
from tests.utils.assertions import assert_wallet


@pytest.fixture
async def wallet_manager(client):
    return WalletManager(client)


async def test_list_wallets(wallet_manager):
    """Позитивная проверка получения списка кошельков"""

    response = await wallet_manager.get_wallets()
    response_json = response.json()

    assert response.status_code == 200
    assert isinstance(response_json, list)

    for wallet in response_json:
        assert_wallet(wallet)
