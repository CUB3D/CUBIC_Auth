"""Add user communication channel

Revision ID: ba5cb70d24fa
Revises: 775659ee27ec
Create Date: 2020-03-27 22:17:01.896702

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba5cb70d24fa'
down_revision = '775659ee27ec'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("User", sa.Column("communication_channel", sa.String(length=32)))


def downgrade():
    op.drop_column("User", "communication_channel")
