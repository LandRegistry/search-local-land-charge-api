"""add service message table

Revision ID: 5ad252086b6c
Revises: 530fd54ad54f
Create Date: 2019-11-08 09:14:39.296169

"""

# revision identifiers, used by Alembic.
revision = '5ad252086b6c'
down_revision = '530fd54ad54f'

import sqlalchemy as sa
from alembic import op
from flask import current_app


def upgrade():
    op.create_table(
        'service_messages',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('message_name', sa.String(), nullable=False),
        sa.Column('message', sa.String(), nullable=False)
    )
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON service_messages TO {};".format(
        current_app.config.get('APP_SQL_USERNAME')))
    op.execute("GRANT ALL ON SEQUENCE service_messages_id_seq TO {};".format(
        current_app.config.get('APP_SQL_USERNAME')))
    # Add permission for acceptance test users
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON service_messages TO {};".format(
        current_app.config.get('ACCTEST_SQL_USERNAME')))
    op.execute("GRANT ALL ON SEQUENCE service_messages_id_seq TO {};".format(
        current_app.config.get('ACCTEST_SQL_USERNAME')))


def downgrade():
    op.execute("REVOKE ALL PRIVILEGES ON SEQUENCE service_messages_id_seq FROM {};".format(
        current_app.config.get("APP_SQL_USERNAME")))
    op.execute("REVOKE ALL PRIVILEGES ON service_messages FROM {};".format(
        current_app.config.get('APP_SQL_USERNAME')))
    op.execute("REVOKE ALL PRIVILEGES ON SEQUENCE service_messages_id_seq FROM {};".format(
        current_app.config.get("ACCTEST_SQL_USERNAME")))
    op.execute("REVOKE ALL PRIVILEGES ON service_messages FROM {};".format(
        current_app.config.get('ACCTEST_SQL_USERNAME')))
    op.drop_table('service_messages')
