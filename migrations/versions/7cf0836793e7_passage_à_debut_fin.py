"""Passage à debut_fin

Revision ID: 7cf0836793e7
Revises: cc024e52500f
Create Date: 2025-04-28 10:51:12.082500

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7cf0836793e7'
down_revision = 'cc024e52500f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('contrat', schema=None) as batch_op:
        batch_op.drop_column('duree')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('contrat', schema=None) as batch_op:
        batch_op.add_column(sa.Column('duree', sa.INTEGER(), nullable=False))

    # ### end Alembic commands ###
