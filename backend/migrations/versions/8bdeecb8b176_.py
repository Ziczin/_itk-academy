"""empty message

Revision ID: 8bdeecb8b176
Revises:
Create Date: 2025-12-21 17:00:54.171407

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8bdeecb8b176"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "wallets",
        sa.Column("uuid", sa.String(), nullable=False),
        sa.Column("balance", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("uuid"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("wallets")
