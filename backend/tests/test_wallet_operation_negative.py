import pytest
from test_services.manager import WalletManager
from tests.utils.assertions import (assert_detail_is_amount_gt_0_validation,
                                    assert_detail_is_insufficient_funds,
                                    assert_wallet)


@pytest.fixture
async def wallet_manager(client):
    return WalletManager(client)


@pytest.fixture
async def wallet_id(wallet_manager):
    """Создание нового кошелька для последующих проверок"""

    response = await wallet_manager.post_wallets(json={})
    response_json = response.json()

    assert response.status_code == 201
    assert_wallet(response_json)

    return response_json["wallet_id"]


def _first_error(response_json: dict) -> dict:
    detail = response_json["detail"]
    assert isinstance(detail, list)
    assert len(detail) >= 1
    return detail[0]


async def test_wallet_withdraw_insufficient_funds(wallet_manager, wallet_id):
    """Негативная проверка: списание при недостаточном балансе"""

    response = await wallet_manager.post_wallet_operation(
        wallet_id,
        json={"operation_type": "WITHDRAW", "amount": 10**12},
    )
    response_json = response.json()

    assert response.status_code in (
        400,
        409,
    ), f"Неожиданный статус ответа: {response.status_code}, тело ответа: {response.text}"
    assert_detail_is_insufficient_funds(response_json)


@pytest.mark.parametrize(
    "operation_type",
    ["DEPOSIT", "WITHDRAW"],
    ids=["deposit_zero_amount", "withdraw_zero_amount"],
)
async def test_wallet_operation_amount_zero_validation(
    wallet_manager, wallet_id, operation_type
):
    """Негативная проверка: amount=0 должен возвращать 422 и валидационную ошибку"""

    response = await wallet_manager.post_wallet_operation(
        wallet_id,
        json={"operation_type": operation_type, "amount": 0},
    )
    response_json = response.json()

    assert (
        response.status_code == 422
    ), f"Неожиданный статус ответа: {response.status_code}, тело ответа: {response.text}"
    assert_detail_is_amount_gt_0_validation(response_json)


@pytest.mark.parametrize(
    "bad_operation_type",
    ["TRANSFER", "deposit", "", " DEPOSIT ", "dEPOSIT"],
    ids=[
        "unknown_TRANSFER",
        "lowercase_deposit",
        "empty_string",
        "spaces_around",
        "mixed_case",
    ],
)
async def test_wallet_operation_invalid_operation_type(
    wallet_manager, wallet_id, bad_operation_type
):
    """Негативная проверка: невалидный operation_type должен возвращать 422"""

    payload = {"operation_type": bad_operation_type, "amount": 10}

    response = await wallet_manager.post_wallet_operation(wallet_id, json=payload)
    response_json = response.json()
    first = _first_error(response_json)

    assert (
        response.status_code == 422
    ), f"Неожиданный статус ответа: {response.status_code}, тело ответа: {response.text}"
    assert first["type"] == "enum"
    assert first["loc"] == ["body", "operation_type"]
    assert first["msg"] == "Input should be 'DEPOSIT' or 'WITHDRAW'"
    assert first["input"] == bad_operation_type
    assert first["ctx"]["expected"] == "'DEPOSIT' or 'WITHDRAW'"


async def test_wallet_operation_missing_operation_type(wallet_manager, wallet_id):
    """Негативная проверка: отсутствие operation_type должно возвращать 422"""

    payload = {"amount": 10}

    response = await wallet_manager.post_wallet_operation(wallet_id, json=payload)
    response_json = response.json()
    first = _first_error(response_json)

    assert (
        response.status_code == 422
    ), f"Неожиданный статус ответа: {response.status_code}, тело ответа: {response.text}"
    assert first["loc"] == ["body", "operation_type"]
    assert first["input"] == payload


async def test_wallet_operation_amount_negative(wallet_manager, wallet_id):
    """Негативная проверка: отрицательный amount должен возвращать 422"""

    payload = {"operation_type": "DEPOSIT", "amount": -1}

    response = await wallet_manager.post_wallet_operation(wallet_id, json=payload)
    response_json = response.json()
    first = _first_error(response_json)

    assert (
        response.status_code == 422
    ), f"Неожиданный статус ответа: {response.status_code}, тело ответа: {response.text}"
    assert first["type"] == "greater_than"
    assert first["loc"] == ["body", "amount"]
    assert first["msg"] == "Input should be greater than 0"
    assert first["input"] == -1
    assert first["ctx"]["gt"] == 0.0


async def test_wallet_operation_amount_empty_string(wallet_manager, wallet_id):
    """Негативная проверка: amount='' должен возвращать 422"""

    payload = {"operation_type": "DEPOSIT", "amount": ""}

    response = await wallet_manager.post_wallet_operation(wallet_id, json=payload)
    response_json = response.json()
    first = _first_error(response_json)

    assert (
        response.status_code == 422
    ), f"Неожиданный статус ответа: {response.status_code}, тело ответа: {response.text}"
    assert first["type"] == "int_parsing"
    assert first["loc"] == ["body", "amount"]
    assert (
        first["msg"]
        == "Input should be a valid integer, unable to parse string as an integer"
    )
    assert first["input"] == ""


async def test_wallet_operation_empty_body(wallet_manager, wallet_id):
    """Негативная проверка: пустое тело {} должно возвращать 422"""

    response = await wallet_manager.post_wallet_operation(wallet_id, json={})
    response_json = response.json()
    first = _first_error(response_json)

    assert (
        response.status_code == 422
    ), f"Неожиданный статус ответа: {response.status_code}, тело ответа: {response.text}"
    assert first["loc"][0] == "body"


async def test_wallet_operation_without_body(wallet_manager, wallet_id):
    """Негативная проверка: отсутствие тела запроса должно возвращать 422"""

    response = await wallet_manager.client.post(f"api/v1/wallets/{wallet_id}/operation")
    response_json = response.json()
    first = _first_error(response_json)

    assert (
        response.status_code == 422
    ), f"Неожиданный статус ответа: {response.status_code}, тело ответа: {response.text}"
    assert first["loc"][0] == "body"

async def test_wallet_operation_amount_exceed_bigint(wallet_manager, wallet_id):
    """Негативная проверка: значение больше BIGINT должно возвращать 422"""

    exceeding_amount = 2**63  # Значение больше максимального для BIGINT
    payload = {"operation_type": "DEPOSIT", "amount": exceeding_amount}

    response = await wallet_manager.post_wallet_operation(wallet_id, json=payload)
    response_json = response.json()

    assert response.status_code == 422, f"Неожиданный статус ответа: {response.status_code}, тело ответа: {response.text}"
    
    first = _first_error(response_json)
    
    assert first['loc'] == ['body', 'amount']
    assert first['msg'] == 'Input should be less than or equal to 9223372036854775807'
    assert first['input'] == exceeding_amount
    assert first['ctx']['le'] == 9223372036854775807


async def test_wallet_operation_amount_bigint_plus_one(wallet_manager, wallet_id):
    """Негативная проверка: максимальное значение BIGINT + 1 должно возвращать 422"""

    max_bigint = 2**63 - 1  # Максимальное значение для BIGINT
    exceeding_amount = max_bigint + 1

    payload = {"operation_type": "DEPOSIT", "amount": exceeding_amount}

    response = await wallet_manager.post_wallet_operation(wallet_id, json=payload)
    response_json = response.json()

    assert response.status_code == 422, f"Неожиданный статус ответа: {response.status_code}, тело ответа: {response.text}"

    first = _first_error(response_json)

    assert first['loc'] == ['body', 'amount']
    assert first['msg'] == 'Input should be less than or equal to 9223372036854775807'
    assert first['input'] == exceeding_amount
    assert first['ctx']['le'] == 9223372036854775807
