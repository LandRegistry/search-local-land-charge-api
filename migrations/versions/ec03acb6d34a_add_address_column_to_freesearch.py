"""Add address column to freesearch

Revision ID: ec03acb6d34a
Revises: d329e76743b8
Create Date: 2022-09-16 12:30:48.585350

"""

# revision identifiers, used by Alembic.
revision = 'ec03acb6d34a'
down_revision = 'd329e76743b8'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column('free_search', sa.Column('address', sa.String(), nullable=True))

def downgrade():
    op.drop_column('free_search', 'address')
