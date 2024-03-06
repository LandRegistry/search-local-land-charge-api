"""add date to free search

Revision ID: 71f1c8ead2c8
Revises: 27fedc81313d
Create Date: 2019-07-03 14:29:22.227297

"""

# revision identifiers, used by Alembic.
revision = '71f1c8ead2c8'
down_revision = '27fedc81313d'

from datetime import datetime

import sqlalchemy as sa
from alembic import op
from dateutil.relativedelta import relativedelta


def upgrade():
    default_time = str(datetime.now() - relativedelta(years=50))

    op.add_column('free_search', sa.Column('search_date', sa.DateTime(),
                                           server_default=default_time))
    op.alter_column('free_search', 'search_date', nullable=False, server_default=None)


def downgrade():
    op.drop_column('free_search', 'search_date')
