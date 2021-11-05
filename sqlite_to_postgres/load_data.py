import os
import sqlite3
import psycopg2
import logging
from dotenv import load_dotenv
from sqlite_loader import SQLiteLoader
from postgres_saver import PostgresSaver
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

logging.basicConfig(level=logging.INFO)
load_dotenv()


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)

    data = sqlite_loader.load_movies()
    postgres_saver.save_all_data(data)


if __name__ == "__main__":
    dsn = {
        "dbname": os.environ.get("DB_NAME"),
        "user": os.environ.get("DB_USER"),
        "password": os.environ.get("DB_PASSWORD"),
        "host": os.environ.get("DB_HOST"),
        "port": os.environ.get("DB_PORT"),
    }
    with sqlite3.connect("db.sqlite") as sqlite_conn, psycopg2.connect(**dsn, cursor_factory=DictCursor) as psql_conn:
        load_from_sqlite(sqlite_conn, psql_conn)
