"""Add restaurant recommendations and dated comments."""

import sqlalchemy as sa
from alembic import op

revision = "004_feedback"
down_revision = "003_restaurants"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("restaurants", sa.Column("recommend", sa.Boolean(), nullable=True))
    op.create_table(
        "comments",
        sa.Column("comment_id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column(
            "restaurant_id",
            sa.Integer(),
            sa.ForeignKey("restaurants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("added_on", sa.Date(), server_default=sa.func.current_date(), nullable=False),
        sa.CheckConstraint("comment ~ '[^[:space:]]'", name="ck_comments_nonblank"),
    )


def downgrade() -> None:
    op.drop_table("comments")
    op.drop_column("restaurants", "recommend")
