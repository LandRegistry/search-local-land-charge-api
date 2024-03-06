"""Add search-status-api table

Revision ID: d329e76743b8
Revises: 6c2511c0927c
Create Date: 2022-06-01 10:40:10.366939

"""

import sqlalchemy as sa
# revision identifiers, used by Alembic.
from alembic import op
from flask import current_app
from geoalchemy2 import types
from sqlalchemy.dialects import postgresql

revision = 'd329e76743b8'
down_revision = '6c2511c0927c'

# revision identifiers, used by Alembic.


def upgrade():
    op.create_table('search_status_search',
                    sa.Column('_id', sa.BigInteger(), nullable=False),
                    sa.Column('search_date', sa.DateTime(), nullable=False),
                    sa.Column('organisation', sa.String(), nullable=False),
                    sa.Column('display_name', sa.String(), nullable=False),
                    sa.Column('charge_ids', postgresql.JSONB(), nullable=False),
                    sa.Column('search_geom', types.Geometry(srid=27700), nullable=False),
                    sa.PrimaryKeyConstraint('_id')
                    )

    op.create_table('search_query',
                    sa.Column('id', sa.BigInteger(), primary_key=True),
                    sa.Column('request_timestamp', sa.DateTime(), nullable=False),
                    sa.Column('completion_timestamp', sa.DateTime(), nullable=True),
                    sa.Column('userid', sa.String(), nullable=False),
                    sa.Column('document', sa.String(), nullable=True),
                    sa.Column('external_url', sa.String(), nullable=True),
                    sa.Column('status', sa.String(), nullable=False))

    op.execute("GRANT SELECT, INSERT ON search_status_search TO {};".format(
        current_app.config.get("APP_SQL_USERNAME")))
    op.execute("GRANT USAGE, SELECT ON SEQUENCE search_status_search__id_seq TO {};".format(
        current_app.config.get('APP_SQL_USERNAME')))
    op.execute("GRANT ALL ON search_query TO " + current_app.config.get("APP_SQL_USERNAME"))
    op.execute("GRANT ALL ON SEQUENCE search_query_id_seq TO {};".format(current_app.config.get('APP_SQL_USERNAME')))


def downgrade():
    op.execute("REVOKE ALL PRIVILEGES ON SEQUENCE search_status_search__id_seq FROM {};".format(
        current_app.config.get("APP_SQL_USERNAME")))
    op.execute("REVOKE ALL PRIVILEGES ON search_status_search FROM {};".format(
        current_app.config.get("APP_SQL_USERNAME")))
    op.drop_table('search_status_search')
    op.execute("REVOKE ALL PRIVILEGES ON SEQUENCE search_query_id_seq FROM {};".format(
        current_app.config.get("APP_SQL_USERNAME")))
    op.execute("REVOKE ALL PRIVILEGES ON search_query FROM {};".format(
        current_app.config.get("APP_SQL_USERNAME")))
    op.drop_table('search_query')

