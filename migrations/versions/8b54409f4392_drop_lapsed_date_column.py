"""drop lapsed date column

Revision ID: 8b54409f4392
Revises: e6f8a376ddae
Create Date: 2018-12-17 10:21:53.635958

"""

# revision identifiers, used by Alembic.
revision = '8b54409f4392'
down_revision = 'e6f8a376ddae'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.drop_column('search_history', 'lapsed_date')
    op.execute("DROP FUNCTION expire_searches()")


def downgrade():
    op.add_column('search_history', sa.Column('lapsed_date', sa.DateTime(), nullable=True))
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
