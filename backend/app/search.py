"""Replaceable place search for the single-process local application."""

import asyncio
from collections import OrderedDict
from time import monotonic

import httpx
from pydantic import BaseModel, TypeAdapter, ValidationError

from app.config import Settings
from app.restaurants import RestaurantCreate


class Place(BaseModel):
    name: str = ""
    display_name: str
    latitude: float | None = None
    longitude: float | None = None
    osm_id: str | None = None


def normalize_place(raw: dict) -> Place:
    place = Place.model_validate(
        {"name": raw.get("name") or "", "display_name": raw.get("display_name") or ""}
    )
    try:
        osm_type = raw.get("osm_type", "")
        osm_number = str(raw.get("osm_id", ""))
        if (
            osm_type not in {"node", "way", "relation"}
            or not osm_number.isascii()
            or not osm_number.isdecimal()
        ):
            return place
        data = RestaurantCreate(
            name=place.name,
            address=place.display_name,
            latitude=float(raw["lat"]),
            longitude=float(raw["lon"]),
            osm_id=f"{osm_type}/{int(osm_number)}",
        )
    except (ValidationError, ValueError, TypeError, KeyError):
        return place
    return place.model_copy(
        update={"latitude": data.latitude, "longitude": data.longitude, "osm_id": data.osm_id}
    )


class PlaceSearch:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.lock = asyncio.Lock()
        self.next_request = 0.0
        self.cache: OrderedDict[str, tuple[float, list[Place]]] = OrderedDict()
        self.client = httpx.AsyncClient(
            timeout=10,
            headers={"User-Agent": settings.nominatim_user_agent},
        )

    async def search(self, query: str) -> list[Place]:
        key = query.casefold()
        # Serialize cache misses across every browser/client of this backend.
        async with self.lock:
            now = monotonic()
            if key in self.cache:
                expires, places = self.cache[key]
                if expires > now:
                    self.cache.move_to_end(key)
                    return places
                del self.cache[key]
            await asyncio.sleep(max(0, self.next_request - now))
            self.next_request = monotonic() + 1.1
            response = await self.client.get(
                self.settings.nominatim_search_url,
                params={
                    "q": query,
                    "format": "jsonv2",
                    "limit": 5,
                    "viewbox": "-71.25,42.45,-70.85,42.20",
                    "bounded": 0,
                    "accept-language": "en",
                },
            )
            # Back off after rate limiting rather than automatically retrying.
            if response.status_code == 429:
                self.next_request = monotonic() + 60
            response.raise_for_status()
            raw_places = TypeAdapter(list[dict]).validate_python(response.json())[:5]
            places = [normalize_place(raw) for raw in raw_places]
            places = list({place.display_name: place for place in places}.values())
            self.cache[key] = (monotonic() + 86400, places)
            if len(self.cache) > 256:
                self.cache.popitem(last=False)
            return places
