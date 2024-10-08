"""add admin_users table

Revision ID: f566ba9c979d
Revises: ca1756b34101
Create Date: 2024-08-03 17:27:44.105525

"""
from alembic import op
import sqlalchemy as sa

from libs.utils import create_password, generate_id
from models import AdminUserModel
from database import SessionLocal


db = SessionLocal()

# revision identifiers, used by Alembic.
revision = 'f566ba9c979d'
down_revision = 'ca1756b34101'
branch_labels = None
depends_on = None

user = {
    "first_name": "Ronak",
    "last_name": "patel",
    "email": "ronakmotka2002@gmail.com",
    "password": "123456"
}


def add_data():
    user["password"] = create_password(user.get("password"))
    db_user = AdminUserModel(
        id=generate_id(),
        **user
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin_users',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=True),
    sa.Column('last_name', sa.String(length=50), nullable=True),
    sa.Column('email', sa.String(length=200), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    add_data()
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('admin_users')
    # ### end Alembic commands ###
