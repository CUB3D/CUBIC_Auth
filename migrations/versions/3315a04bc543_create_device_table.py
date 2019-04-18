"""create_device_table

Revision ID: 3315a04bc543
Revises: f4555d687f35
Create Date: 2019-04-18 01:43:16.756970

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3315a04bc543'
down_revision = 'f4555d687f35'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'Device',
        sa.Column('DeviceID', sa.Integer, primary_key=True),
        sa.Column('DeviceToken', sa.VARCHAR, nullable=False, unique=True),
        sa.Column('DeviceType', sa.VARCHAR, nullable=False),
        sa.Column('OwnerID', sa.Integer, nullable=False),
        sa.Column('BatteryPercent', sa.Integer, default=0),
        sa.Column('Latitude', sa.REAL, default=0.0),
        sa.Column('Longitude', sa.REAL, default=0.0),
        sa.ForeignKeyConstraint(['OwnerID'], ['User.UserID'], ),
    )


def downgrade():
    op.drop_table('Device')
