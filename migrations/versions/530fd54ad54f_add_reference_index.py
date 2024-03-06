"""Add reference index

Revision ID: 530fd54ad54f
Revises: d456d0db8c8e
Create Date: 2019-11-06 12:43:41.158460

"""

# revision identifiers, used by Alembic.
revision = '530fd54ad54f'
down_revision = 'd456d0db8c8e'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.create_index('ix_search_history_reference', 'search_history', ['reference'])


def downgrade():
    op.drop_index('ix_search_history_reference')
