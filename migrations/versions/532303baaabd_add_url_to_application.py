"""add_url_to_application

Revision ID: 532303baaabd
Revises: 3315a04bc543
Create Date: 2019-04-18 01:53:27.979976

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '532303baaabd'
down_revision = '3315a04bc543'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('Application', sa.Column('url', sa.VARCHAR(128), nullable=False, server_default="https://auth.cub3d.pw"))


def downgrade():
    op.drop_column('Application', 'url')
