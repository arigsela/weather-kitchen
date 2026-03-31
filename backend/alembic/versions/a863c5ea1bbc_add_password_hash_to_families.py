"""add password_hash to families

Revision ID: a863c5ea1bbc
Revises: 454939a8f035
Create Date: 2026-03-31 07:51:50.795569

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a863c5ea1bbc'
down_revision: Union[str, None] = '454939a8f035'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add password_hash column
    op.add_column('families', sa.Column('password_hash', sa.String(length=128), nullable=True))
    # Make admin_pin_hash nullable (SQLite requires batch mode for ALTER COLUMN)
    with op.batch_alter_table('families') as batch_op:
        batch_op.alter_column('admin_pin_hash', existing_type=sa.VARCHAR(length=128), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('families') as batch_op:
        batch_op.alter_column('admin_pin_hash', existing_type=sa.VARCHAR(length=128), nullable=False)
    op.drop_column('families', 'password_hash')
