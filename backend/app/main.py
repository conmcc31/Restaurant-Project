from contextlib import asynccontextmanager
from typing import Annotated

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.config import Settings
from app.search import Place, PlaceSearch


def create_app() -> FastAPI:
    settings = Settings()
    search = PlaceSearch(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            yield
        finally:
            await search.client.aclose()

    app = FastAPI(title="Food Maps", lifespan=lifespan)
    app.state.place_search = search
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_methods=["GET"],
        allow_headers=["Content-Type"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/places/search", response_model=list[Place])
    async def search_places(q: Annotated[str, Query(max_length=200)]):
        query = " ".join(q.split())
        if not query:
            return []
        try:
            return await search.search(query)
        except (httpx.HTTPError, ValidationError, ValueError):
            raise HTTPException(
                status_code=503, detail="Location search is unavailable. Please try again later."
            ) from None

    return app
