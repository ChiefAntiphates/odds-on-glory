"""empty message

Revision ID: d9f19a40c518
Revises: d0953330fe46
Create Date: 2020-06-28 20:47:30.050199

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9f19a40c518'
down_revision = 'd0953330fe46'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('bonus_available', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('last_bonus', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_bonus')
    op.drop_column('user', 'bonus_available')
    # ### end Alembic commands ###
