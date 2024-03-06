"""Update type of lapsed field from bool to datetime and change its name to lapsed_date

Revision ID: d4474d91fbfa
Revises: e691b0ecde96
Create Date: 2018-03-15 13:29:10.149319

"""

# revision identifiers, used by Alembic.
revision = 'd4474d91fbfa'
down_revision = 'e691b0ecde96'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.drop_column('search_history', 'lapsed')
    op.add_column('search_history', sa.Column('lapsed_date', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('search_history', 'lapsed_date')
    op.add_column('search_history', sa.Column('lapsed', sa.Boolean(), nullable=False))