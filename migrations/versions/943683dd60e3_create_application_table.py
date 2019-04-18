"""create_application_table

Revision ID: 943683dd60e3
Revises: b0e4078fa087
Create Date: 2019-04-18 01:30:34.911826

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '943683dd60e3'
down_revision = 'b0e4078fa087'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'Application',
        sa.Column('ApplicationID', sa.Integer, primary_key=True),
        sa.Column('ApplicationToken', sa.VARCHAR, nullable=False, unique=True),
        sa.Column('CreationTime', sa.Integer, nullable=False),
        sa.Column('OwnerID', sa.Integer, nullable=False),
        sa.Column('Description', sa.VARCHAR, nullable=False),
        sa.Column('ApplicationName', sa.VARCHAR, nullable=False),
        sa.ForeignKeyConstraint(['OwnerID'], ['User.UserID'], ),
    )


def downgrade():
    op.drop_table('Application')
