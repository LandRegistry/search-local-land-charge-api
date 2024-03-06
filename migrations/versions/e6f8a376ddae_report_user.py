"""Create user for report runner and additional column

Revision ID: e6f8a376ddae
Revises: 31538f30d875
Create Date: 2018-05-18 10:46:42.113122

"""

# revision identifiers, used by Alembic.
revision = 'e6f8a376ddae'
down_revision = '31538f30d875'

import sqlalchemy as sa
from alembic import op
from flask import current_app


def upgrade():
    query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '{0}') THEN CREATE ROLE {0} " \
            "WITH LOGIN PASSWORD '{1}'; END IF; END $$;".format(current_app.config.get("FINANCE_REPORT_SQL_USERNAME"),
                                                                current_app.config.get("FINANCE_REPORT_SQL_PASSWORD"))
    op.execute(query)

    op.execute("GRANT SELECT ON search_history TO {};".format(
        current_app.config.get("FINANCE_REPORT_SQL_USERNAME")))

    op.add_column('search_history',  sa.Column('reference', sa.String(), nullable=True))


def downgrade():
    query = "DO $$ BEGIN IF EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '{0}') " \
            "THEN " \
            "REVOKE ALL PRIVILEGES ON search_history FROM {0}; " \
            "REVOKE ALL PRIVILEGES ON search_history_search_id_seq FROM {0}; " \
            "DROP ROLE {0}; " \
            "END IF; END $$;".format(current_app.config.get("FINANCE_REPORT_SQL_USERNAME"))

    op.execute(query)

    op.drop_column('search_history', 'reference')
