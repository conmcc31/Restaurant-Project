"""Verify configured PostgreSQL connectivity without creating any tables."""

import sys

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.config import Settings


def main() -> int:
    settings = Settings()
    engine = create_engine(settings.database_url, connect_args={"connect_timeout": 5})
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar_one()
            if result != 1:
                print("Database check returned an unexpected result.", file=sys.stderr)
                return 1
        print("Database connection successful (SELECT 1).")
        return 0
    except SQLAlchemyError:
        # Avoid logging the URL, password, or driver connection details.
        print(
            "Database connection failed. Check backend/.env and PostgreSQL readiness.",
            file=sys.stderr,
        )
        return 1
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
