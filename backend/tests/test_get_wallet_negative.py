import uuid

import pytest
from test_services.manager import WalletManager


@pytest.fixture
async def wallet_manager(client):
    return WalletManager(client)


@pytest.mark.parametrize(
    "invalid_wallet_id",
    [
        "123",
        "not-a-uuid",
        "%%%%",
        "0000",
    ],
    ids=[
        "numeric_string",
        "random_string",
        "special_chars",
        "short_string",
    ],
)
async def test_get_wallet_invalid_uuid(wallet_manager, invalid_wallet_id):
    """Негативная проверка: невалидный UUID в path"""

    response = await wallet_manager.get_wallet(invalid_wallet_id)
    response_json = response.json()

    assert (
        response.status_code == 422
    ), f"Неожиданный статус ответа: {response.status_code}, тело ответа: {response.text}"

    detail = response_json.get("detail")

    assert isinstance(detail, list)
    assert len(detail) >= 1

    first_error = detail[0]

    assert first_error.get("type") == "uuid_parsing"
    assert first_error.get("loc") == ["path", "wallet_uuid"]
    assert "Input should be a valid UUID" in first_error.get("msg")


async def test_get_wallet_not_found(wallet_manager):
    """Негативная проверка: кошелёк с валидным UUID не существует"""

    not_existing_wallet_id = str(uuid.uuid4())

    response = await wallet_manager.get_wallet(not_existing_wallet_id)
    response_json = response.json()

    assert response.status_code == 404
    assert response_json.get("detail") == "Wallet not found"
