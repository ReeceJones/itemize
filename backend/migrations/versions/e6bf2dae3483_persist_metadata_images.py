"""Persist metadata images

Revision ID: e6bf2dae3483
Revises: 1e13d09b8661
Create Date: 2023-10-02 20:52:36.987183

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6bf2dae3483'
down_revision: Union[str, None] = '1e13d09b8661'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('metadataimage', schema=None) as batch_op:
        batch_op.alter_column('data',
               existing_type=sa.BLOB(),
               nullable=True)
       #  batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('page_metadata_id')

    with op.batch_alter_table('pagemetadata', schema=None) as batch_op:
        batch_op.add_column(sa.Column('price', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('currency', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('image_id', sa.Integer(), nullable=True))
        batch_op.alter_column('image_url',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('description',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('site_name',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.create_foreign_key('fk_image_id_id', 'metadataimage', ['image_id'], ['id'])

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pagemetadata', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('site_name',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('description',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('image_url',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.drop_column('image_id')
        batch_op.drop_column('currency')
        batch_op.drop_column('price')

    with op.batch_alter_table('metadataimage', schema=None) as batch_op:
        batch_op.add_column(sa.Column('page_metadata_id', sa.INTEGER(), nullable=False))
        batch_op.create_foreign_key(None, 'pagemetadata', ['page_metadata_id'], ['id'])
        batch_op.alter_column('data',
               existing_type=sa.BLOB(),
               nullable=False)

    # ### end Alembic commands ###
