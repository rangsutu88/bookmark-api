"""empty message

Revision ID: cef0957f4422
Revises: 9585568b8c79
Create Date: 2016-09-28 12:03:12.000731

"""

# revision identifiers, used by Alembic.
revision = 'cef0957f4422'
down_revision = '9585568b8c79'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.add_column('user', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'user', 'role', ['role_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_column('user', 'role_id')
    op.drop_table('role')
    ### end Alembic commands ###