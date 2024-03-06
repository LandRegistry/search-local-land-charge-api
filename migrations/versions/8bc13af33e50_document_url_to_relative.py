"""document_url to relative

Revision ID: 8bc13af33e50
Revises: 395281f76568
Create Date: 2021-02-11 15:08:37.907840

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = '8bc13af33e50'
down_revision = '395281f76568'


def upgrade():
    op.alter_column('search_history', 'document_url', nullable=True, new_column_name='document_url_old')
    op.add_column('search_history', sa.Column('document_url', sa.String(), nullable=True))
    op.execute("UPDATE search_history SET document_url = "
               "regexp_replace(document_url_old, "
               "'https?:\/\/[^\/:]+(:[0-9]+)?\/v1\.0\/storage\/([^\/]+)\/([^\/]+)', '/\\2/\\3');")


def downgrade():
    op.drop_column('search_history', 'document_url')
    op.alter_column('search_history', 'document_url_old', nullable=True, new_column_name='document_url')
