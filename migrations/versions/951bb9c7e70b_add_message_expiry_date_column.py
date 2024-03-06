"""add message expiry date column

Revision ID: 951bb9c7e70b
Revises: a80948ac7861
Create Date: 2023-04-20 12:22:28.140908

"""

# revision identifiers, used by Alembic.
revision = '951bb9c7e70b'
down_revision = 'a80948ac7861'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column('service_messages', sa.Column('message_expiry_date', sa.Date(), nullable=True))


def downgrade():
    op.drop_column('service_messages', 'message_expiry_date')
