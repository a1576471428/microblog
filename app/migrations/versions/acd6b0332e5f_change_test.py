"""change test

Revision ID: acd6b0332e5f
Revises: 439af973eb72
Create Date: 2017-05-13 22:54:45.831653

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'acd6b0332e5f'
down_revision = '439af973eb72'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('nickname', sa.String(length=64), nullable=True))
    op.drop_index('username', table_name='user')
    op.create_unique_constraint(None, 'user', ['nickname'])
    op.drop_column('user', 'username')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('username', mysql.VARCHAR(length=80), nullable=True))
    op.drop_constraint(None, 'user', type_='unique')
    op.create_index('username', 'user', ['username'], unique=True)
    op.drop_column('user', 'nickname')
    # ### end Alembic commands ###
