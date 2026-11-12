"""Replaceable place search for the single-process local application."""

import asyncio
from collections import OrderedDict
from time import monotonic

import httpx
from pydantic import BaseModel, TypeAdapter

from app.config import Settings


class Place(BaseModel):
    name: str = ""
    display_name: str


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
            places = TypeAdapter(list[Place]).validate_python(response.json())[:5]
            places = list({place.display_name: place for place in places}.values())
            self.cache[key] = (monotonic() + 86400, places)
            if len(self.cache) > 256:
                self.cache.popitem(last=False)
            return places
