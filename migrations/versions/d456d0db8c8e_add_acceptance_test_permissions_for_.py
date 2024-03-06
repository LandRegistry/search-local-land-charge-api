"""Add acceptance test permissions for free_search table

Revision ID: d456d0db8c8e
Revises: 4e708c5b002a
Create Date: 2019-10-16 15:51:17.143496

"""

# revision identifiers, used by Alembic.
revision = 'd456d0db8c8e'
down_revision = '4e708c5b002a'

import sqlalchemy as sa
from alembic import op
from flask import current_app


def upgrade():
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON free_search TO {};".format(
        current_app.config.get("ACCTEST_SQL_USERNAME")))
    op.execute("GRANT SELECT, USAGE ON free_search__id_seq TO {};".format(
        current_app.config.get("ACCTEST_SQL_USERNAME")))


def downgrade():
    op.execute("REVOKE ALL PRIVILEGES ON free_search FROM {0};".format(current_app.config.get("ACCTEST_SQL_USERNAME")))
    op.execute("REVOKE ALL PRIVILEGES ON free_search__id_seq FROM {0};".format(current_app.config.get("ACCTEST_SQL_USERNAME")))
