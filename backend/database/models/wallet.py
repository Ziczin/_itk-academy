from database.db import Base
from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column


class Wallet(Base):
    __tablename__ = "wallets"

    uuid: Mapped[str] = mapped_column(primary_key=True)
    balance: Mapped[int] = mapped_column(BigInteger, default=0)
