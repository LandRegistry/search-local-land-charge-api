"""Initial database structure for search history

Revision ID: acfb38fa7591
Revises: None
Create Date: 2018-02-19 13:35:13.431571

"""

import sqlalchemy as sa
from alembic import op
from flask import current_app
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'acfb38fa7591'
down_revision = None


def upgrade():
    op.create_table('search_history',
                    sa.Column('search_id', sa.BigInteger(), primary_key=True),
                    sa.Column('user_id', sa.String(), nullable=False),
                    sa.Column('charges', postgresql.JSONB(), nullable=False),
                    sa.Column('search_extent', postgresql.JSONB(), nullable=False),
                    sa.Column('lapsed', sa.Boolean(), nullable=False),
                    sa.Column('document_url', sa.String(), nullable=False),
                    sa.Column('parent_search_id', sa.ForeignKey('search_history.search_id'), nullable=False))
    op.create_index('ix_search_history_search_id', 'search_history', ['search_id'])
    op.execute("GRANT SELECT, INSERT ON search_history TO " + current_app.config.get("APP_SQL_USERNAME"))
    pass


def downgrade():
    op.drop_index('ix_search_history_search_id')
    op.drop_table('search_history')
