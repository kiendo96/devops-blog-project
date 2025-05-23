"""Add featured_image_url to Post

Revision ID: 47263746444f
Revises: 6795f1f1abc1
Create Date: 2025-05-05 11:07:47.049185

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '47263746444f'
down_revision = '6795f1f1abc1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('featured_image_url', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_column('featured_image_url')

    # ### end Alembic commands ###
