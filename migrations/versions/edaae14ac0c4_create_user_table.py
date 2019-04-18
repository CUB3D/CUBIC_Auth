"""create_user_table

Revision ID: edaae14ac0c4
Revises: 
Create Date: 2019-04-17 00:43:15.218311

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'edaae14ac0c4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'User',
        sa.Column('UserID', sa.Integer, primary_key=True),
        sa.Column('Username', sa.Unicode(50), nullable=False, unique=True),
        sa.Column('PasswordHash', sa.VARCHAR, nullable=False),
    )


def downgrade():
    op.drop_table('User')
