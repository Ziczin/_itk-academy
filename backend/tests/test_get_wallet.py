import pytest
from test_services.manager import WalletManager
from tests.utils.assertions import assert_wallet


@pytest.fixture
async def wallet_manager(client):
    return WalletManager(client)


async def test_get_wallet_by_id(wallet_manager):
    """Позитивная проверка получения информации по кошельку"""

    create_response = await wallet_manager.post_wallets(json={})
    create_response_json = create_response.json()
    wallet_id = create_response_json.get("wallet_id")

    assert create_response.status_code == 201
    assert_wallet(create_response_json)

    get_response = await wallet_manager.get_wallet(wallet_id)
    get_response_json = get_response.json()

    assert get_response.status_code == 200
    assert_wallet(get_response_json)
    assert get_response_json["wallet_id"] == wallet_id
