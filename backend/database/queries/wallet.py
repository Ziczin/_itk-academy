from uuid import UUID

from database.models.wallet import Wallet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..locking import acquire_lock


async def add_wallet(
    db: AsyncSession, wallet_uuid: UUID, initial_balance: int = 0
) -> Wallet:
    wallet = Wallet(uuid=str(wallet_uuid), balance=initial_balance)
    db.add(wallet)
    await db.commit()
    await db.refresh(wallet)
    return wallet


async def get_wallet(db: AsyncSession, wallet_uuid: UUID) -> Wallet:
    result = await db.execute(select(Wallet).where(Wallet.uuid == str(wallet_uuid)))
    wallet = result.scalar_one_or_none()
    return wallet


async def update_wallet_balance(
    db: AsyncSession, wallet_uuid: UUID, operation_type: str, amount: float
) -> Wallet:
    async with acquire_lock(db, Wallet, str(wallet_uuid), "uuid") as wallet:
        if operation_type == "WITHDRAW":
            if wallet.balance < amount:
                raise ValueError("Недостаточно средств")
            wallet.balance -= amount
        else:
            new_balance = wallet.balance + amount

            if new_balance > 9_223_372_036_854_775_807:
                raise ValueError("Баланс превышает максимально допустимое значение")

            wallet.balance = new_balance

        return wallet
