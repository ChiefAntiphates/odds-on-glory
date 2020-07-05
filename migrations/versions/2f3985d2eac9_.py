"""empty message

Revision ID: 2f3985d2eac9
Revises: 2ea88eaec051
Create Date: 2020-07-02 10:09:12.156223

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f3985d2eac9'
down_revision = '2ea88eaec051'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_gladiator_battle_ready'), 'gladiator', ['battle_ready'], unique=False)
    op.create_index(op.f('ix_gladiator_elims'), 'gladiator', ['elims'], unique=False)
    with op.batch_alter_table('gladiator') as batch_op:
	    batch_op.drop_column('last_fight')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('gladiator', sa.Column('last_fight', sa.DATETIME(), nullable=True))
    op.drop_index(op.f('ix_gladiator_elims'), table_name='gladiator')
    op.drop_index(op.f('ix_gladiator_battle_ready'), table_name='gladiator')
    # ### end Alembic commands ###