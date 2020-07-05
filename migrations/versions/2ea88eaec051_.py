"""empty message

Revision ID: 2ea88eaec051
Revises: 368554b2c5b2
Create Date: 2020-07-02 09:55:08.048754

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ea88eaec051'
down_revision = '368554b2c5b2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('gladiator', sa.Column('battle_ready', sa.Integer(), nullable=True))
    op.add_column('gladiator', sa.Column('elims', sa.Integer(), nullable=True))
    op.add_column('gladiator', sa.Column('last_fight', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_gladiator_elims'), 'gladiator', ['elims'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_gladiator_elims'), table_name='gladiator')
    op.drop_index(op.f('ix_gladiator_battle_ready'), table_name='gladiator')
    op.drop_column('gladiator', 'last_fight')
    op.drop_column('gladiator', 'elims')
    op.drop_column('gladiator', 'battle_ready')
    # ### end Alembic commands ###
