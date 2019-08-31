"""create_user_application_table

Revision ID: f4555d687f35
Revises: 943683dd60e3
Create Date: 2019-04-18 01:35:06.067078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4555d687f35'
down_revision = '943683dd60e3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'UserApplication',
        sa.Column('UserApplicationID', sa.Integer, primary_key=True),
        sa.Column('UserID', sa.Integer, nullable=False),
        sa.Column('ApplicationID', sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(['UserID'], ['User.UserID'], ),
        sa.ForeignKeyConstraint(['ApplicationID'], ['Application.ApplicationID'], ),
    )


def downgrade():
    op.drop_table('UserApplication')
