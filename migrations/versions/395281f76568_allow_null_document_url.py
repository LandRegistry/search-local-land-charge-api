"""Allow null document_url

Revision ID: 395281f76568
Revises: 5ad252086b6c
Create Date: 2020-10-12 15:30:30.757428

"""

# revision identifiers, used by Alembic.
revision = '395281f76568'
down_revision = '5ad252086b6c'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.alter_column('search_history', 'document_url', existing_type=sa.String(), nullable=True)


def downgrade():
    op.alter_column('search_history', 'document_url', existing_type=sa.String(), nullable=False)
