"""New table

Revision ID: c0769f2fc3eb
Revises: 
Create Date: 2024-10-04 17:59:53.316507

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'c0769f2fc3eb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('vehicles', 'make',
               existing_type=mysql.VARCHAR(length=400),
               type_=sa.String(length=250),
               existing_nullable=True)
    op.alter_column('vehicles', 'model',
               existing_type=mysql.VARCHAR(length=400),
               type_=sa.String(length=250),
               existing_nullable=True)
    op.create_index('ix_vehicle_make_model', 'vehicles', ['make', 'model'], unique=False)
    op.create_index('ix_vehicle_price_mileage', 'vehicles', ['listing_price', 'listing_mileage'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_vehicle_price_mileage', table_name='vehicles')
    op.drop_index('ix_vehicle_make_model', table_name='vehicles')
    op.alter_column('vehicles', 'model',
               existing_type=sa.String(length=250),
               type_=mysql.VARCHAR(length=400),
               existing_nullable=True)
    op.alter_column('vehicles', 'make',
               existing_type=sa.String(length=250),
               type_=mysql.VARCHAR(length=400),
               existing_nullable=True)
    # ### end Alembic commands ###
