"""Tables for resolution results

Revision ID: 403ac9cde8bc
Revises: 4db3e31c9b96
Create Date: 2014-07-10 21:54:00.054781

"""

# revision identifiers, used by Alembic.
revision = '403ac9cde8bc'
down_revision = '4db3e31c9b96'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('resolution_result',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('package_id', sa.Integer(), nullable=True),
    sa.Column('resolved', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['package_id'], ['package.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('resolution_result_element',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('resolution_id', sa.Integer(), nullable=True),
    sa.Column('problem', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['resolution_id'], ['resolution_result.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('resolution_result_element')
    op.drop_table('resolution_result')
    ### end Alembic commands ###