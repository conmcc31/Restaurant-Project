"""Unit contracts and migration-backed tests in a newly created disposable database."""

import os
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Boolean, Date, create_engine, event, inspect, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import Settings
from app.main import create_app
from app.models import Base, Comment, Restaurant

PAYLOAD = dict(
    name="Cafe", address="Cafe, Boston", latitude=42.36, longitude=-71.05, osm_id="node/123"
)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://unused:unused@localhost/unused")
    with TestClient(create_app()) as client:
        yield client


@pytest.mark.parametrize(
    "change",
    [
        {"name": " \t\n"},
        {"address": ""},
        {"latitude": 91},
        {"latitude": -91},
        {"longitude": 181},
        {"longitude": -181},
        {"latitude": "NaN"},
        {"latitude": True},
        {"longitude": None},
        {"osm_id": "123"},
        {"osm_id": "node/0"},
        {"osm_id": "way/001"},
        {"osm_id": "place/123"},
        {"osm_id": "node/-1"},
        {"osm_id": "node/1\n"},
        {"user_id": "someone"},
    ],
)
def test_invalid_payload_never_reaches_database(client, change):
    assert client.post("/api/restaurants", json=PAYLOAD | change).status_code == 422


@pytest.mark.parametrize("missing", list(PAYLOAD))
def test_required_fields(client, missing):
    payload = PAYLOAD.copy()
    del payload[missing]
    assert client.post("/api/restaurants", json=payload).status_code == 422


def test_database_error_is_recoverable_and_private(client, monkeypatch):
    def fail(*args):
        raise SQLAlchemyError("secret connection details")

    monkeypatch.setattr("app.main.save_restaurant", fail)
    response = client.post("/api/restaurants", json=PAYLOAD)
    assert response.status_code == 503
    assert response.json() == {"detail": "Restaurant could not be saved. Please try again."}
    assert client.get("/health").status_code == 200


def test_post_cors(client):
    response = client.options(
        "/api/restaurants",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.status_code == 200
    assert "POST" in response.headers["access-control-allow-methods"]


@pytest.fixture
def postgres(monkeypatch, request):
    # Explicit opt-in avoids silently touching development data or requiring a DB for unit tests.
    if os.environ.get("RUN_POSTGRES_TESTS") != "1":
        pytest.skip("Set RUN_POSTGRES_TESTS=1 with local PostgreSQL running")
    admin = create_engine(Settings().database_url, isolation_level="AUTOCOMMIT")
    name = "food_maps_test_" + uuid4().hex
    with admin.connect() as conn:
        conn.execute(text(f'CREATE DATABASE "{name}"'))
    url = admin.url.set(database=name)
    engine = create_engine(url)
    config = Config("alembic.ini")
    try:
        monkeypatch.setenv("DATABASE_URL", url.render_as_string(hide_password=False))
        command.upgrade(config, getattr(request, "param", "head"))
        yield engine, config
    finally:
        engine.dispose()
        with admin.connect() as conn:
            conn.execute(text(f'DROP DATABASE "{name}" WITH (FORCE)'))
        admin.dispose()


def test_postgres_persistence_concurrency_constraints_and_migrations(postgres):
    engine, config = postgres
    with TestClient(create_app()) as client:
        # Concurrent first inserts must return one winner and the same committed row.
        with ThreadPoolExecutor(max_workers=8) as pool:
            responses = list(
                pool.map(lambda _: client.post("/api/restaurants", json=PAYLOAD), range(8))
            )
        assert sorted(r.status_code for r in responses) == [200] * 7 + [201]
        records = [r.json()["restaurant"] for r in responses]
        assert all(r == records[0] for r in records)
        assert records[0] == PAYLOAD | {"user_id": "xyz123", "id": records[0]["id"]}
        assert {r.json()["outcome"] for r in responses} == {"created", "already_saved"}
        duplicate = client.post("/api/restaurants", json=PAYLOAD | {"name": "Changed"})
        assert duplicate.json()["restaurant"]["name"] == "Cafe"
        assert (
            client.post(
                "/api/restaurants",
                json=PAYLOAD | {"osm_id": "way/123", "latitude": -90, "longitude": 180},
            ).status_code
            == 201
        )
        assert (
            client.post(
                "/api/restaurants",
                json=PAYLOAD | {"osm_id": "relation/123", "latitude": 90, "longitude": -180},
            ).status_code
            == 201
        )

    # A failure at commit must roll back the insert and return no false success.
    def reject_commit(session):
        raise SQLAlchemyError("simulated commit failure")

    with TestClient(create_app()) as client:
        event.listen(Session, "before_commit", reject_commit)
        try:
            failed = client.post("/api/restaurants", json=PAYLOAD | {"osm_id": "node/999"})
            assert failed.status_code == 503
        finally:
            event.remove(Session, "before_commit", reject_commit)
        with engine.connect() as conn:
            assert (
                conn.execute(
                    text("SELECT count(*) FROM restaurants WHERE osm_id = 'node/999'")
                ).scalar_one()
                == 0
            )
        assert client.post("/api/restaurants", json=PAYLOAD).json()["outcome"] == "already_saved"
    # Independent connection proves actual commits and migration reruns retain data.
    command.upgrade(config, "head")
    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM restaurants")).scalar_one() == 3
    inspector = inspect(engine)
    assert [c["name"] for c in inspector.get_columns("restaurants") if c["nullable"]] == [
        "recommend"
    ]
    assert inspector.get_pk_constraint("restaurants")["constrained_columns"] == ["id"]
    assert inspector.get_unique_constraints("restaurants")[0]["column_names"] == [
        "user_id",
        "osm_id",
    ]
    assert Base.metadata.tables["restaurants"].columns.keys() == [
        c["name"] for c in inspector.get_columns("restaurants")
    ]
    for assignment in [
        "latitude = 'NaN'",
        "longitude = 'Infinity'",
        "latitude = 91",
        "longitude = -181",
        "name = E' \\t'",
        "address = ''",
        "osm_id = 'node/0'",
        "user_id = 'other'",
        "name = NULL",
        "osm_id = 'way/123'",
    ]:
        with pytest.raises(IntegrityError), engine.begin() as conn:
            conn.execute(text(f"UPDATE restaurants SET {assignment} WHERE osm_id = 'node/123'"))
    # Downgrade only this disposable DB, never the demonstration database.
    command.downgrade(config, "base")
    assert "restaurants" not in inspect(engine).get_table_names()
    command.upgrade(config, "head")
    assert "restaurants" in inspect(engine).get_table_names()


@pytest.mark.parametrize("postgres", ["003_restaurants"], indirect=True)
def test_feedback_upgrade_and_downgrade(postgres):
    engine, config = postgres
    save = text(
        "INSERT INTO restaurants (user_id, name, address, latitude, longitude, osm_id) "
        "VALUES ('xyz123', :name, :address, :latitude, :longitude, :osm_id) RETURNING *"
    )
    with engine.begin() as conn:
        original = dict(conn.execute(save, PAYLOAD).mappings().one())

    command.upgrade(config, "head")
    columns = {c["name"]: c for c in inspect(engine).get_columns("restaurants")}
    assert isinstance(columns["recommend"]["type"], Boolean)
    assert columns["recommend"]["nullable"] and columns["recommend"]["default"] is None
    assert isinstance(inspect(engine).get_columns("comments")[-1]["type"], Date)
    with engine.begin() as conn:
        assert dict(conn.execute(select(Restaurant)).mappings().one()) == original | {
            "recommend": None
        }
        new = conn.execute(save, PAYLOAD | {"osm_id": "way/234"}).mappings().one()
        assert new["recommend"] is None
        for state in (True, False, None):
            states = conn.scalars(
                Restaurant.__table__.update()
                .values(recommend=state)
                .returning(Restaurant.recommend)
            ).all()
            assert states == [state, state]

    with Session(engine) as session, session.begin():
        today = session.scalar(text("SELECT CURRENT_DATE"))
        notes = [
            Comment(restaurant_id=restaurant_id, comment=note)
            for restaurant_id, note in [
                (original["id"], "Outdoor tables"),
                (original["id"], "Try the soup"),
                (new["id"], "Great coffee"),
            ]
        ]
        session.add_all(notes)
        session.flush()
        assert all(note.added_on == today for note in notes)
        survivor_id = notes[-1].comment_id

    insert = Comment.__table__.insert()
    for invalid in [
        {"restaurant_id": -1, "comment": "No parent"},
        {"comment": "Missing restaurant"},
        {"restaurant_id": new["id"]},
        {"restaurant_id": new["id"], "comment": ""},
        {"restaurant_id": new["id"], "comment": " \t\n"},
        {"restaurant_id": new["id"], "comment": "Missing date", "added_on": None},
    ]:
        with pytest.raises(IntegrityError), engine.begin() as conn:
            conn.execute(insert, invalid)

    with engine.begin() as conn:
        conn.execute(Restaurant.__table__.delete().where(Restaurant.id == original["id"]))
        assert conn.execute(select(Comment.comment_id, Comment.comment)).all() == [
            (survivor_id, "Great coffee")
        ]

    command.downgrade(config, "003_restaurants")
    assert "comments" not in inspect(engine).get_table_names()
    assert "recommend" not in {c["name"] for c in inspect(engine).get_columns("restaurants")}
    command.upgrade(config, "head")
    with engine.connect() as conn:
        assert conn.execute(select(Restaurant.id, Restaurant.recommend)).one() == (new["id"], None)
        assert conn.scalars(select(Comment.comment_id)).all() == []
