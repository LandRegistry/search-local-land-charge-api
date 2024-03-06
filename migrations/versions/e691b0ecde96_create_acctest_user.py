"""Creates user with elevated permissions for the acceptance tests.

Revision ID: e691b0ecde96
Revises: 1283940c219d
Create Date: 2018-03-09 11:24:32.943849

"""

# revision identifiers, used by Alembic.
revision = 'e691b0ecde96'
down_revision = '1283940c219d'

from alembic import op
from flask import current_app


def upgrade():
    query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '{0}') THEN CREATE ROLE {0} " \
            "WITH LOGIN PASSWORD '{1}'; END IF; END $$;".format(current_app.config.get("ACCTEST_SQL_USERNAME"),
                                                                current_app.config.get("ACCTEST_SQL_PASSWORD"))
    op.execute(query)

    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON search_history TO {};".format(
        current_app.config.get("ACCTEST_SQL_USERNAME")))
    op.execute("GRANT SELECT, USAGE ON search_history_search_id_seq TO {};".format(
        current_app.config.get("ACCTEST_SQL_USERNAME")))


def downgrade():
    query = "DO $$ BEGIN IF EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '{0}') " \
            "THEN " \
            "REVOKE ALL PRIVILEGES ON search_history FROM {0}; " \
            "REVOKE ALL PRIVILEGES ON search_history_search_id_seq FROM {0}; " \
            "DROP ROLE {0}; " \
            "END IF; END $$;".format(current_app.config.get("ACCTEST_SQL_USERNAME"))

    op.execute(query)
