"""empty message

Revision ID: d0953330fe46
Revises: 9323a7bf5e0d
Create Date: 2020-06-28 09:47:46.673741

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0953330fe46'
down_revision = '9323a7bf5e0d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tournament', sa.Column('density', sa.String(length=16), nullable=True))
    op.add_column('tournament', sa.Column('size', sa.String(length=16), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tournament', 'size')
    op.drop_column('tournament', 'density')
    # ### end Alembic commands ###
