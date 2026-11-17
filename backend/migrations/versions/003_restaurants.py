"""Create restaurants.

Revision ID: 003_restaurants
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "003_restaurants"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "restaurants",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("latitude", sa.Double(), nullable=False),
        sa.Column("longitude", sa.Double(), nullable=False),
        sa.Column("osm_id", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "osm_id", name="uq_restaurants_user_osm"),
        sa.CheckConstraint("user_id = 'xyz123'", name="ck_restaurants_user"),
        sa.CheckConstraint("name ~ '[^[:space:]]'", name="ck_restaurants_name"),
        sa.CheckConstraint("address ~ '[^[:space:]]'", name="ck_restaurants_address"),
        sa.CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_restaurants_latitude"),
        sa.CheckConstraint("longitude BETWEEN -180 AND 180", name="ck_restaurants_longitude"),
        sa.CheckConstraint(
            "osm_id ~ '^(node|way|relation)/[1-9][0-9]*$'", name="ck_restaurants_osm_id"
        ),
    )


def downgrade() -> None:
    op.drop_table("restaurants")
