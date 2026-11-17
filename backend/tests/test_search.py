import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.search import PlaceSearch


@pytest.fixture
def settings(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://unused:unused@localhost/unused")
    return Settings()


def test_search_contract_and_cache(settings):
    calls = []

    def upstream(request):
        calls.append(request)
        return httpx.Response(
            200,
            json=[
                {
                    "name": "Cafe",
                    "display_name": "Cafe, Boston",
                    "lat": "42.36",
                    "lon": "-71.05",
                    "osm_type": "node",
                    "osm_id": 123,
                }
            ],
        )

    async def run():
        service = PlaceSearch(settings)
        await service.client.aclose()
        service.client = httpx.AsyncClient(
            transport=httpx.MockTransport(upstream),
            headers={"User-Agent": settings.nominatim_user_agent},
        )
        first, second = await asyncio.gather(service.search("Cafe"), service.search("cafe"))
        assert first == second
        assert first[0].display_name == "Cafe, Boston"
        assert first[0].osm_id == "node/123"
        assert first[0].latitude == 42.36
        await service.client.aclose()

    asyncio.run(run())
    assert len(calls) == 1
    assert calls[0].headers["User-Agent"] == settings.nominatim_user_agent
    assert calls[0].url.params["limit"] == "5"
    assert calls[0].url.params["bounded"] == "0"
    assert "viewbox" in calls[0].url.params


def test_concurrent_requests_are_spaced_even_after_failure(settings, monkeypatch):
    now = [100.0]
    starts = []

    async def sleep(delay):
        now[0] += delay

    def upstream(request):
        starts.append(now[0])
        return httpx.Response(500 if len(starts) == 1 else 200, json=[])

    monkeypatch.setattr("app.search.monotonic", lambda: now[0])
    monkeypatch.setattr("app.search.asyncio.sleep", sleep)

    async def run():
        service = PlaceSearch(settings)
        await service.client.aclose()
        service.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
        results = await asyncio.gather(
            service.search("First"), service.search("Second"), return_exceptions=True
        )
        assert isinstance(results[0], httpx.HTTPStatusError)
        assert results[1] == []
        await service.client.aclose()

    asyncio.run(run())
    assert starts[1] - starts[0] >= 1


@pytest.mark.parametrize(
    "payload,status,expected",
    [([], 200, 200), ({"invalid": True}, 200, 503), ([], 429, 503), ([], 500, 503)],
)
def test_api_empty_and_provider_failures(settings, payload, status, expected):
    app = create_app()
    with TestClient(app) as client:
        service = app.state.place_search
        service.client = httpx.AsyncClient(
            transport=httpx.MockTransport(lambda request: httpx.Response(status, json=payload))
        )
        assert client.get("/api/places/search", params={"q": "Cafe"}).status_code == expected
        assert client.get("/api/places/search", params={"q": "  "}).json() == []
        assert client.get("/api/places/search", params={"q": "x" * 201}).status_code == 422


def test_normalizes_provider_identity_and_coordinates():
    from app.search import normalize_place

    raw = dict(
        name="Cafe",
        display_name="Cafe, Boston",
        lat="42.36",
        lon="-71.05",
        osm_type="way",
        osm_id=123,
        place_id=999,
    )
    place = normalize_place(raw)
    assert place.osm_id == "way/123"
    assert place.latitude == 42.36
    assert place.longitude == -71.05
    assert normalize_place(raw | {"osm_type": "node", "osm_id": "00123"}).osm_id == "node/123"
    for change in [
        {"name": ""},
        {"display_name": ""},
        {"lat": "NaN"},
        {"lon": "181"},
        {"osm_id": None},
        {"osm_type": "unknown"},
        {"osm_id": 0},
    ]:
        result = normalize_place(raw | change)
        assert result.osm_id is None
        assert result.latitude is None
        assert result.name == (raw | change)["name"]
    assert (
        normalize_place({"name": "Cafe", "display_name": "Boston", "place_id": 999}).osm_id is None
    )
