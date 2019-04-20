"""create_location_history_table

Revision ID: aa6a596ffeb6
Revises: 532303baaabd
Create Date: 2019-04-20 05:20:42.266428

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa6a596ffeb6'
down_revision = '532303baaabd'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'LocationHistory',
        sa.Column('ID', sa.Integer, primary_key=True),
        sa.Column('DeviceID', sa.Integer, nullable=False),
        sa.Column('Latitude', sa.REAL, nullable=False, default=0.0),
        sa.Column('Longitude', sa.REAL, nullable=False, default=0.0),
        sa.Column('CreationTime', sa.Integer, nullable=False)
    )


def downgrade():
    op.drop_table('LocationHistory')
