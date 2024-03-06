"""Add stored procedure which expires all searches older than 6 months

Revision ID: 7f9630d794d8
Revises: d4474d91fbfa
Create Date: 2018-04-11 14:29:36.064680

"""

# revision identifiers, used by Alembic.
revision = '7f9630d794d8'
down_revision = 'd4474d91fbfa'

from alembic import op


def upgrade():
    op.execute(
        """
        CREATE FUNCTION expire_searches()
        RETURNS void AS $$
        BEGIN
          UPDATE search_history 
          SET lapsed_date = NOW()::timestamp where search_date < NOW()::timestamp - INTERVAL '6 months';
        END
        $$ LANGUAGE plpgsql;
        """
    )


def downgrade():
    op.execute("DROP FUNCTION expire_searches()")