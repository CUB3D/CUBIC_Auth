""" Add token to user application table

Revision ID: c2f5f456f13a
Revises: aa6a596ffeb6
Create Date: 2019-08-13 10:45:44.330432

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2f5f456f13a'
down_revision = 'aa6a596ffeb6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('UserApplication', sa.Column('token', sa.VARCHAR(128), nullable=False, server_default="", unique=True))


def downgrade():
    op.drop_column("UserApplication", "token")
