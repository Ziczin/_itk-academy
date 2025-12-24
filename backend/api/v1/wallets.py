import uuid
from typing import List

from database.db import get_db
from database.queries.wallet import (add_wallet, get_wallet,
                                     update_wallet_balance)
from database.schemas.wallets import (OperationResponse, WalletBalanceResponse,
                                      WalletOperation)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

wallets_router = APIRouter(prefix="/wallets", tags=["wallets"])


@wallets_router.get("/", response_model=List[WalletBalanceResponse])
async def get_wallet_list(db: AsyncSession = Depends(get_db)):
    from database.models.wallet import Wallet
    from sqlalchemy import select

    result = await db.execute(select(Wallet))
    wallets = result.scalars().all()

    return [
        WalletBalanceResponse(wallet_id=uuid.UUID(w.uuid), balance=w.balance)
        for w in wallets
    ]


@wallets_router.get("/{wallet_uuid}", response_model=WalletBalanceResponse)
async def get_wallet_by_uuid(
    wallet_uuid: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    wallet = await get_wallet(db, wallet_uuid)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
        )

    return WalletBalanceResponse(
        wallet_id=uuid.UUID(wallet.uuid), balance=wallet.balance
    )


@wallets_router.post("/{wallet_uuid}/operation", response_model=OperationResponse)
async def wallet_operation(
    wallet_uuid: uuid.UUID,
    operation: WalletOperation,
    db: AsyncSession = Depends(get_db),
):
    try:
        wallet = await update_wallet_balance(
            db, wallet_uuid, operation.operation_type, operation.amount
        )

        return OperationResponse(
            wallet_id=uuid.UUID(wallet.uuid),
            operation_type=operation.operation_type,
            amount=operation.amount,
            new_balance=wallet.balance,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@wallets_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_wallet(db: AsyncSession = Depends(get_db)):
    new_uuid = uuid.uuid4()
    wallet = await add_wallet(db, new_uuid)

    return WalletBalanceResponse(
        wallet_id=uuid.UUID(wallet.uuid), balance=wallet.balance
    )
