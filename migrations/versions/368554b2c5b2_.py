"""empty message

Revision ID: 368554b2c5b2
Revises: d9f19a40c518
Create Date: 2020-06-30 14:59:39.703416

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '368554b2c5b2'
down_revision = 'd9f19a40c518'
branch_labels = None
depends_on = None


def upgrade():
	with op.batch_alter_table('user') as batch_op:
		batch_op.drop_column('bonus_available')


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('bonus_available', sa.BOOLEAN(), nullable=True))
    # ### end Alembic commands ###
