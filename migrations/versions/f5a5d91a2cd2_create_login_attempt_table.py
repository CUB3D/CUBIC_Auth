"""create_login_attempt_table

Revision ID: f5a5d91a2cd2
Revises: a565f0b413f6
Create Date: 2019-04-17 18:43:18.242434

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5a5d91a2cd2'
down_revision = 'a565f0b413f6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'LoginAttempt',
        sa.Column('AttemptID', sa.Integer, primary_key=True),
        sa.Column('Username', sa.VARCHAR(128), nullable=False),
        sa.Column('AccessTime', sa.Integer, nullable=False),
        sa.Column('Success', sa.Integer, nullable=False),
    )


def downgrade():
    op.drop_table('LoginAttempt')
