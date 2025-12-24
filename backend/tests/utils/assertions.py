import uuid


def assert_wallet(wallet: dict) -> None:
    wallet_id = wallet.get("wallet_id")
    balance = wallet.get("balance")

    assert isinstance(wallet, dict)
    assert isinstance(wallet_id, str)
    uuid.UUID(wallet_id)
    assert isinstance(balance, (int, float))


def assert_operation_success(
    response_json: dict,
    *,
    wallet_id: str,
    operation_type: str,
    amount: float,
) -> None:
    assert isinstance(response_json, dict)
    assert response_json.get("wallet_id") == wallet_id
    assert response_json.get("operation_type") == operation_type
    assert isinstance(response_json.get("amount"), (int, float))
    assert float(response_json.get("amount")) == float(amount)
    assert response_json.get("status") == "success"
    assert isinstance(response_json.get("new_balance"), (int, float))


def assert_detail_is_insufficient_funds(response_json: dict) -> None:
    assert isinstance(response_json, dict)
    assert response_json.get("detail") == "Недостаточно средств"


def assert_detail_is_amount_gt_0_validation(response_json: dict) -> None:
    assert isinstance(response_json, dict)
    detail = response_json.get("detail")

    assert isinstance(detail, list)
    assert len(detail) >= 1

    first = detail[0]
    assert first.get("type") == "greater_than"
    assert first.get("loc") == ["body", "amount"]
    assert first.get("msg") == "Input should be greater than 0"
    assert first.get("input") == 0
    ctx = first.get("ctx")
    assert isinstance(ctx, dict)
    assert ctx.get("gt") == 0.0
