from contextlib import asynccontextmanager
from typing import Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)


@asynccontextmanager
async def acquire_lock(
    db: AsyncSession, model_class: Type[ModelType], record_id, id_column: str = "id"
):
    async with db.begin():
        stmt = (
            select(model_class)
            .where(getattr(model_class, id_column) == record_id)
            .with_for_update()
        )

        result = await db.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            raise ValueError(f"Record not found: {record_id}")

        yield record
