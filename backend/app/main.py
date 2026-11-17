from contextlib import asynccontextmanager
from typing import Annotated

import httpx
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import Settings
from app.restaurants import RestaurantCreate, SaveResult, save_restaurant
from app.search import Place, PlaceSearch


def create_app() -> FastAPI:
    settings = Settings()
    search = PlaceSearch(settings)
    engine = create_engine(settings.database_url, connect_args={"connect_timeout": 5})

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            yield
        finally:
            await search.client.aclose()
            engine.dispose()

    app = FastAPI(title="Food Maps", lifespan=lifespan)
    app.state.place_search = search
    app.state.engine = engine
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_methods=["GET", "POST"],
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

    @app.post(
        "/api/restaurants",
        response_model=SaveResult,
        status_code=201,
        responses={200: {"model": SaveResult}, 503: {"description": "Save unavailable"}},
    )
    def create_restaurant(payload: RestaurantCreate, response: Response):
        try:
            with Session(app.state.engine) as session:
                result = save_restaurant(session, payload)
            response.status_code = 201 if result.outcome == "created" else 200
            return result
        except SQLAlchemyError:
            raise HTTPException(
                status_code=503, detail="Restaurant could not be saved. Please try again."
            ) from None

    return app
