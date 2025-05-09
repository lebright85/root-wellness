"""Update Class.teacher backref to taught_classes

Revision ID: d99a8487ecf5
Revises: 3d0a5a54d11f
Create Date: 2025-05-09 08:56:14.525393

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd99a8487ecf5'
down_revision = '3d0a5a54d11f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('attendee', schema=None) as batch_op:
        batch_op.alter_column('group',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('comments',
               existing_type=sa.VARCHAR(length=200),
               type_=sa.Text(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('attendee', schema=None) as batch_op:
        batch_op.alter_column('comments',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=200),
               existing_nullable=True)
        batch_op.alter_column('group',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=50),
               existing_nullable=True)

    # ### end Alembic commands ###
