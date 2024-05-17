"""create ezfuel tables

Revision ID: cc43094c4526
Revises: 
Create Date: 2024-05-16 20:06:45.559482

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc43094c4526'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('drivers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('cell_number', sa.String(length=15), nullable=False),
    sa.Column('license_no', sa.String(), nullable=False),
    sa.Column('_ssn', sa.String(), nullable=False),
    sa.Column('ssn_last_4', sa.String(length=4), nullable=False),
    sa.Column('license_plate', sa.String(), nullable=False),
    sa.Column('mailing_address', sa.String(), nullable=False),
    sa.Column('current_location', sa.String(), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('_password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_drivers')),
    sa.UniqueConstraint('email', name=op.f('uq_drivers_email'))
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('cell_number', sa.String(length=15), nullable=True),
    sa.Column('mailing_address', sa.String(), nullable=True),
    sa.Column('_cars', sa.JSON(), nullable=True),
    sa.Column('current_location', sa.String(), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('_password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('email', name=op.f('uq_users_email'))
    )
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('driver_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('fuel_type', sa.String(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('ppg', sa.Float(), nullable=False),
    sa.Column('total', sa.Float(), nullable=False),
    sa.Column('total_payout', sa.Float(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('license_plate', sa.String(), nullable=False),
    sa.Column('order_location', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['driver_id'], ['drivers.id'], name=op.f('fk_orders_driver_id_drivers')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_orders_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_orders'))
    )
    op.create_table('payment_methods',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('_card_number', sa.String(), nullable=False),
    sa.Column('card_number_last_4', sa.String(length=4), nullable=False),
    sa.Column('_cvv', sa.String(), nullable=False),
    sa.Column('expiration_date', sa.String(length=5), nullable=False),
    sa.Column('postal_code', sa.String(length=20), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_payment_methods_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_payment_methods'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('payment_methods')
    op.drop_table('orders')
    op.drop_table('users')
    op.drop_table('drivers')
    # ### end Alembic commands ###