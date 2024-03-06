"""Add welsh service messages

Revision ID: 6c2511c0927c
Revises: 8bc13af33e50
Create Date: 2021-10-06 16:10:19.738174

"""

# revision identifiers, used by Alembic.
revision = '6c2511c0927c'
down_revision = '8bc13af33e50'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column('service_messages', sa.Column('message_cy', sa.String(), nullable=True))
    op.execute("UPDATE service_messages SET message_cy = message")
    op.alter_column('service_messages', 'message_cy', nullable=False)
    op.alter_column('service_messages', 'message', nullable=False, new_column_name='message_en')

def downgrade():
    op.alter_column('service_messages', 'message_en', nullable=False, new_column_name='message')
    op.drop_column('service_messages', 'message_cy')
