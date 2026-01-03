import os
import sqlite3
import psycopg2
import logging
from contextlib import closing
from dotenv import load_dotenv, find_dotenv
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

try:
    from .sqlite_loader import SQLiteLoader
    from .postgres_saver import PostgresSaver
except ImportError:  # если запускаешь из папки sqlite_to_postgres
    from sqlite_loader import SQLiteLoader
    from postgres_saver import PostgresSaver


logging.basicConfig(level=logging.INFO)
load_dotenv(find_dotenv())


def load_from_sqlite(sqlite_cursor: sqlite3.Cursor, pg_conn: _connection) -> None:
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(sqlite_cursor)

    data = sqlite_loader.load_movies()
    postgres_saver.save_all_data(data)


def _build_dsn() -> dict:
    required = ["DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        raise RuntimeError(f"missing required env vars: {', '.join(missing)}")

    return {
        "dbname": os.environ.get("DB_NAME"),
        "user": os.environ.get("DB_USER"),
        "password": os.environ.get("DB_PASSWORD"),
        "host": os.environ.get("DB_HOST"),
        "port": os.environ.get("DB_PORT"),
    }


if __name__ == "__main__":
    dsn = _build_dsn()
    sqlite_path = os.path.join(os.path.dirname(__file__), "db.sqlite")

    with psycopg2.connect(**dsn, cursor_factory=DictCursor) as psql_conn:
        with closing(sqlite3.connect(sqlite_path)) as sqlite_conn:
            sqlite_cursor = sqlite_conn.cursor()
            load_from_sqlite(sqlite_cursor, psql_conn)
