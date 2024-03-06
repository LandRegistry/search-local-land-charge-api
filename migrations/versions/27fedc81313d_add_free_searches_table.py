"""Add free searches table

Revision ID: 27fedc81313d
Revises: 8b54409f4392
Create Date: 2019-02-04 15:47:04.583375

"""

# revision identifiers, used by Alembic.
revision = '27fedc81313d'
down_revision = '8b54409f4392'

import sqlalchemy as sa
from alembic import op
from flask import current_app
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table('free_search',
                    sa.Column('_id', sa.BigInteger(), nullable=False),
                    sa.Column('user_id', sa.String(), nullable=False),
                    sa.Column('charge_ids', postgresql.JSONB(), nullable=False),
                    sa.Column('search_extent', postgresql.JSONB(), nullable=False),
                    sa.PrimaryKeyConstraint('_id')
                    )

    op.execute("GRANT SELECT, INSERT ON free_search TO {};".format(
        current_app.config.get("APP_SQL_USERNAME")))
    op.execute("GRANT USAGE, SELECT ON SEQUENCE free_search__id_seq TO {};".format(
        current_app.config.get('APP_SQL_USERNAME')))


def downgrade():
    op.execute("REVOKE ALL PRIVILEGES ON SEQUENCE free_search__id_seq FROM {};".format(
        current_app.config.get("APP_SQL_USERNAME")))
    op.execute("REVOKE ALL PRIVILEGES ON free_search FROM {};".format(
        current_app.config.get("APP_SQL_USERNAME")))
    op.drop_table('free_search')
