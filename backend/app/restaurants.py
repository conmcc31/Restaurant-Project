"""Validated save contract and transactional PostgreSQL persistence."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import Restaurant

Nonblank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
OsmIdentity = Annotated[str, StringConstraints(pattern=r"^(node|way|relation)/[1-9][0-9]*$")]


class RestaurantCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Nonblank
    address: Nonblank
    latitude: float = Field(ge=-90, le=90, allow_inf_nan=False, strict=True)
    longitude: float = Field(ge=-180, le=180, allow_inf_nan=False, strict=True)
    osm_id: OsmIdentity


class RestaurantRecord(RestaurantCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: str


class SaveResult(BaseModel):
    outcome: Literal["created", "already_saved"]
    restaurant: RestaurantRecord


def save_restaurant(session: Session, payload: RestaurantCreate) -> SaveResult:
    # ON CONFLICT waits for concurrent inserts before reading the committed winner.
    # DO NOTHING also preserves the original restaurant data on repeat selection.
    with session.begin():
        row = session.scalars(
            insert(Restaurant)
            .values(user_id="xyz123", **payload.model_dump())
            .on_conflict_do_nothing(constraint="uq_restaurants_user_osm")
            .returning(Restaurant)
        ).one_or_none()
        outcome = "created" if row is not None else "already_saved"
        if row is None:
            row = session.scalars(
                select(Restaurant).where(
                    Restaurant.user_id == "xyz123", Restaurant.osm_id == payload.osm_id
                )
            ).one()
        result = SaveResult(outcome=outcome, restaurant=RestaurantRecord.model_validate(row))
    # Returning only after the transaction exits ensures commit failures cannot report success.
    return result
