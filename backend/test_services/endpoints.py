WALLETS = "api/v1/wallets/"
WALLET_BY_ID = "api/v1/wallets/{wallet_id}"
WALLET_OPERATION = "api/v1/wallets/{wallet_id}/operation"


def wallet_by_id(wallet_id: str) -> str:
    return WALLET_BY_ID.format(wallet_id=wallet_id)


def wallet_operation(wallet_id: str) -> str:
    return WALLET_OPERATION.format(wallet_id=wallet_id)
