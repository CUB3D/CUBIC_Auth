"""Remove LocationHistory

Revision ID: 1cd0fbae2241
Revises: c2f5f456f13a
Create Date: 2020-03-27 22:08:05.623739

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1cd0fbae2241'
down_revision = 'c2f5f456f13a'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("LocationHistory")


def downgrade():
    pass
