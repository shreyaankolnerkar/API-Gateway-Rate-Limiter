"""remove upstream_service from request_logs

Revision ID: e7f70366b399
Revises: d1b8099c8700
Create Date: 2026-02-11 11:37:55.687965

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "e7f70366b399"
down_revision: Union[str, Sequence[str], None] = "d1b8099c8700"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
