"""Add build_opts column

Revision ID: c9c6e92946b
Revises: 3770b40e6ef8
Create Date: 2014-07-22 00:07:58.501762

"""

# revision identifiers, used by Alembic.
revision = 'c9c6e92946b'
down_revision = '3770b40e6ef8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('package', sa.Column('build_opts', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('package', 'build_opts')
    ### end Alembic commands ###
