"""Add search datetime column and payment_id column to search history table

Revision ID: 1283940c219d
Revises: acfb38fa7591
Create Date: 2018-03-01 10:37:50.385135

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1283940c219d'
down_revision = 'acfb38fa7591'


def upgrade():
    op.add_column('search_history', sa.Column('search_date', sa.DateTime(), nullable=False))
    op.add_column('search_history',  sa.Column('payment_id', sa.String(), nullable=False))
    op.alter_column('search_history', 'charges', existing_type=postgresql.JSONB(), nullable=True)
    op.alter_column('search_history', 'parent_search_id', existing_type=sa.BigInteger(), nullable=True)


def downgrade():
    op.drop_column('search_history', 'search_date')
    op.drop_column('search_history', 'payment_id')
    op.alter_column('search_history', 'charges', existing_type=postgresql.JSONB(), nullable=False)
    op.alter_column('search_history', 'parent_search_id', existing_type=sa.BigInteger(), nullable=False)
