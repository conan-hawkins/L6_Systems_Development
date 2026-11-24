"""require lowercase email

Revision ID: 01bcb4fd8630
Revises: 7c53873d1a2c
Create Date: 2026-11-19 12:55:36.782062

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01bcb4fd8630'
down_revision = '7c53873d1a2c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint("ck_users_email_lowercase", "users", "email = lower(email)")


def downgrade():
    op.drop_constraint("ck_users_email_lowercase", "users", type_="check")
