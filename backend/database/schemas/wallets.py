from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"  # Пополнение
    WITHDRAW = "WITHDRAW"  # Списание


class WalletOperation(BaseModel):
    """Операция изменения баланса"""

    operation_type: OperationType
    amount: int = Field(..., gt=0, le=9_223_372_036_854_775_807)


class WalletBalanceResponse(BaseModel):
    """Ответ с балансом"""

    wallet_id: UUID
    balance: int


class OperationResponse(BaseModel):
    """Ответ на операцию"""

    wallet_id: UUID
    operation_type: OperationType
    amount: int
    new_balance: int
    status: str = "success"
