"""Remove uneeded device columns

Revision ID: 775659ee27ec
Revises: 1cd0fbae2241
Create Date: 2020-03-27 22:13:58.929695

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '775659ee27ec'
down_revision = '1cd0fbae2241'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("Device", "BatteryPercent")
    op.drop_column("Device", "Latitude")
    op.drop_column("Device", "Longitude")


def downgrade():
    pass
