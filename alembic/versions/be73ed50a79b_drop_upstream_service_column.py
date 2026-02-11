"""drop upstream_service column

Revision ID: be73ed50a79b
Revises: e7f70366b399
Create Date: 2026-02-11 11:51:43.460766

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "be73ed50a79b"
down_revision: Union[str, Sequence[str], None] = "e7f70366b399"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
