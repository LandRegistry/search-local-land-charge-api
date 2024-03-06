"""Add additional service message columns

Revision ID: a80948ac7861
Revises: 3218688b32d1
Create Date: 2023-01-16 16:28:04.716294

"""

# revision identifiers, used by Alembic.
revision = 'a80948ac7861'
down_revision = '3218688b32d1'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column('service_messages', sa.Column('hyperlink_message_en', sa.String(), nullable=True))
    op.add_column('service_messages', sa.Column('hyperlink_message_cy', sa.String(), nullable=True))
    op.add_column('service_messages', sa.Column('hyperlink_link_en', sa.String(), nullable=True))
    op.add_column('service_messages', sa.Column('hyperlink_link_cy', sa.String(), nullable=True))

def downgrade():
    op.drop_column('service_messages', 'hyperlink_message_en')
    op.drop_column('service_messages', 'hyperlink_message_cy')
    op.drop_column('service_messages', 'hyperlink_link_en')
    op.drop_column('service_messages', 'hyperlink_link_cy')
