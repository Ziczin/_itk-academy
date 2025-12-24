import pytest
from test_services.manager import WalletManager
from tests.utils.assertions import assert_operation_success, assert_wallet


@pytest.fixture
async def wallet_manager(client):
    return WalletManager(client)


@pytest.fixture
async def wallet_id(wallet_manager):
    """Создание нового кошелька для последующих проверок"""

    create_response = await wallet_manager.post_wallets(json={})
    create_response_json = create_response.json()
    created_wallet_id = create_response_json.get("wallet_id")

    assert create_response.status_code == 201
    assert_wallet(create_response_json)

    return created_wallet_id


async def test_wallet_operation_deposit_success(wallet_manager, wallet_id):
    """Позитивная проверка: пополнение кошелька"""

    response = await wallet_manager.post_wallet_operation(
        wallet_id,
        json={"operation_type": "DEPOSIT", "amount": 10},
    )
    response_json = response.json()

    assert response.status_code == 200
    assert_operation_success(
        response_json,
        wallet_id=wallet_id,
        operation_type="DEPOSIT",
        amount=10.0,
    )


async def test_wallet_operation_withdraw_success(wallet_manager, wallet_id):
    """Позитивная проверка: списание после предварительного пополнения"""

    deposit_response = await wallet_manager.post_wallet_operation(
        wallet_id,
        json={"operation_type": "DEPOSIT", "amount": 10},
    )
    deposit_response_json = deposit_response.json()

    withdraw_response = await wallet_manager.post_wallet_operation(
        wallet_id,
        json={"operation_type": "WITHDRAW", "amount": 1},
    )
    withdraw_response_json = withdraw_response.json()

    assert deposit_response.status_code == 200
    assert_operation_success(
        deposit_response_json,
        wallet_id=wallet_id,
        operation_type="DEPOSIT",
        amount=10.0,
    )

    assert withdraw_response.status_code == 200
    assert_operation_success(
        withdraw_response_json,
        wallet_id=wallet_id,
        operation_type="WITHDRAW",
        amount=1.0,
    )

async def test_wallet_operation_amount_bigint(wallet_manager, wallet_id):
    """Позитивная проверка: Проверка корректной работы с BIGINT значением"""

    big_int_amount = 2**63 - 1  # Максимальное значение для BIGINT
    payload = {"operation_type": "DEPOSIT", "amount": big_int_amount}

    response = await wallet_manager.post_wallet_operation(wallet_id, json=payload)
    response_json = response.json()

    assert response.status_code == 200, f"Неожиданный статус ответа: {response.status_code}, тело ответа: {response.text}"
    assert response_json['amount'] == big_int_amount
