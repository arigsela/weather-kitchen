"""jwt_auth_add_refresh_tokens_remove_api_token_hash

Revision ID: 454939a8f035
Revises: 251d1db8a18d
Create Date: 2026-02-18 10:56:48.346509

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '454939a8f035'
down_revision: Union[str, None] = '251d1db8a18d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add refresh_tokens table for JWT refresh token storage
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('family_id', sa.String(36), nullable=False),
        sa.Column('token_hash', sa.String(64), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['family_id'], ['families.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_refresh_tokens_family_id', 'refresh_tokens', ['family_id'], unique=False)
    op.create_index('ix_refresh_tokens_token_hash', 'refresh_tokens', ['token_hash'], unique=True)

    # Remove legacy API token columns from families
    op.drop_index('ix_families_api_token_hash', table_name='families')
    op.drop_column('families', 'api_token_hash')
    op.drop_column('families', 'token_created_at')

    # Remove leftover COPPA columns (from original schema, pivot removed them from model)
    with op.batch_alter_table('families') as batch_op:
        for col in ('consent_given', 'parent_email', 'has_minor_users',
                    'consent_code_expires_at', 'consent_date', 'consent_code_hash'):
            try:
                batch_op.drop_column(col)
            except Exception:
                pass  # column may already be absent in this environment


def downgrade() -> None:
    op.drop_index('ix_refresh_tokens_token_hash', table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_family_id', table_name='refresh_tokens')
    op.drop_table('refresh_tokens')

    op.add_column('families', sa.Column('api_token_hash', sa.String(64), nullable=False, server_default=''))
    op.add_column('families', sa.Column('token_created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.create_index('ix_families_api_token_hash', 'families', ['api_token_hash'], unique=True)
