"""Added index to free searches

Revision ID: 3218688b32d1
Revises: ec03acb6d34a
Create Date: 2022-10-27 11:31:56.664541

"""

# revision identifiers, used by Alembic.
revision = '3218688b32d1'
down_revision = 'ec03acb6d34a'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.create_index('idx_user_id_free_search', 'free_search', ['user_id'])
    op.create_index('idx_search_date_free_search', 'free_search', ['search_date'])


def downgrade():
    op.drop_index('idx_user_id_free_search')
    op.drop_index('idx_search_date_free_search')
