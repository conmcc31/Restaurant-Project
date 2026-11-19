"""Restaurant schema. Tables are created only through Alembic."""

from datetime import date

from sqlalchemy import (
    CheckConstraint,
    Double,
    ForeignKey,
    Identity,
    Integer,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Restaurant(Base):
    __tablename__ = "restaurants"
    __table_args__ = (
        UniqueConstraint("user_id", "osm_id", name="uq_restaurants_user_osm"),
        CheckConstraint("user_id = 'xyz123'", name="ck_restaurants_user"),
        CheckConstraint("name ~ '[^[:space:]]'", name="ck_restaurants_name"),
        CheckConstraint("address ~ '[^[:space:]]'", name="ck_restaurants_address"),
        CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_restaurants_latitude"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="ck_restaurants_longitude"),
        CheckConstraint(
            "osm_id ~ '^(node|way|relation)/[1-9][0-9]*$'", name="ck_restaurants_osm_id"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    user_id: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    address: Mapped[str] = mapped_column(Text)
    latitude: Mapped[float] = mapped_column(Double)
    longitude: Mapped[float] = mapped_column(Double)
    osm_id: Mapped[str] = mapped_column(Text)
    recommend: Mapped[bool | None] = mapped_column()


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (CheckConstraint("comment ~ '[^[:space:]]'", name="ck_comments_nonblank"),)

    comment_id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id", ondelete="CASCADE"))
    comment: Mapped[str] = mapped_column(Text)
    added_on: Mapped[date] = mapped_column(server_default=func.current_date())
