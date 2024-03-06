"""Add additional fields for payment information

Revision ID: 31538f30d875
Revises: 3417d4818da1
Create Date: 2018-05-11 09:52:37.679707

"""

# revision identifiers, used by Alembic.
revision = '31538f30d875'
down_revision = '3417d4818da1'

import sqlalchemy as sa
from alembic import op
from flask import current_app


def upgrade():
    op.add_column('search_history',  sa.Column('card_brand', sa.String(), nullable=True))
    op.add_column('search_history',  sa.Column('payment_provider', sa.String(), nullable=True))
    op.add_column('search_history',  sa.Column('amount', sa.Integer(), nullable=True))
    op.alter_column('search_history', 'user_id', existing_type=sa.String(), nullable=True)
    op.execute("GRANT UPDATE ON search_history TO " + current_app.config.get("APP_SQL_USERNAME"))


def downgrade():
    op.drop_column('search_history', 'card_brand')
    op.drop_column('search_history', 'payment_provider')
    op.drop_column('search_history', 'amount')
    op.alter_column('search_history', 'user_id', existing_type=sa.String(), nullable=False)
    op.execute("REVOKE UPDATE ON search_history FROM " + current_app.config.get("APP_SQL_USERNAME"))
