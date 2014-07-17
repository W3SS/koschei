"""Remove PackageStateChange

Revision ID: 3770b40e6ef8
Revises: 34641b5a09a3
Create Date: 2014-07-17 16:51:46.123498

"""

# revision identifiers, used by Alembic.
revision = '3770b40e6ef8'
down_revision = '34641b5a09a3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table(u'package_change')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(u'package_change',
    sa.Column(u'id', sa.INTEGER(), server_default="nextval('package_change_id_seq'::regclass)", nullable=False),
    sa.Column(u'prev_state', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column(u'curr_state', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column(u'applied_in_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column(u'package_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['applied_in_id'], [u'build.id'], name=u'package_change_applied_in_id_fkey'),
    sa.ForeignKeyConstraint(['package_id'], [u'package.id'], name=u'package_change_package_id_fkey'),
    sa.PrimaryKeyConstraint(u'id', name=u'package_change_pkey')
    )
    ### end Alembic commands ###
