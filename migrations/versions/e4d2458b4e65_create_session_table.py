"""create_session_table

Revision ID: e4d2458b4e65
Revises: edaae14ac0c4
Create Date: 2019-04-17 00:45:08.571061

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4d2458b4e65'
down_revision = 'edaae14ac0c4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'Session',
        sa.Column('SessionID', sa.Integer, primary_key=True),
        sa.Column('SessionToken', sa.VARCHAR(128), nullable=False, unique=True),
        sa.Column('UserID', sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(['UserID'], ['User.UserID'], ),
    )


def downgrade():
    op.drop_table('Session')
