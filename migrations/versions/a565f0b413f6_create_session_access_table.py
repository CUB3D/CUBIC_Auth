"""create_session_access_table

Revision ID: a565f0b413f6
Revises: e4d2458b4e65
Create Date: 2019-04-17 17:54:05.602253

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a565f0b413f6'
down_revision = 'e4d2458b4e65'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'SessionAccess',
        sa.Column('UsageID', sa.Integer, primary_key=True),
        sa.Column('SessionID', sa.Integer, nullable=False),
        sa.Column('AccessTime', sa.Integer, nullable=False),
        sa.Column('Success', sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(['SessionID'], ['Session.SessionID'], ),
    )


def downgrade():
    op.drop_table('SessionAccess')
