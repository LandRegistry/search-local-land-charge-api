"""Adding search area description column

Revision ID: 3417d4818da1
Revises: 7f9630d794d8
Create Date: 2018-04-18 11:54:56.090883

"""

# revision identifiers, used by Alembic.
revision = '3417d4818da1'
down_revision = '7f9630d794d8'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column('search_history',  sa.Column('search_area_description', sa.String(length=1000), nullable=True))


def downgrade():
    op.drop_column('search_history', 'search_area_description')
