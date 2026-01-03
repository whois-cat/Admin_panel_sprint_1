from __future__ import annotations

import logging
import sqlite3
from dataclasses import asdict
from typing import Dict, Iterable, Iterator, List, Type

from .db_classes import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork


logger = logging.getLogger(__name__)

TABLE_TO_DATACLASS: Dict[str, Type] = {
    "genre": Genre,
    "person": Person,
    "film_work": FilmWork,
    "genre_film_work": GenreFilmWork,
    "person_film_work": PersonFilmWork,
}


class SQLiteLoader:
    """Reads rows from SQLite and converts them into dicts.
    The dict keys match dataclass field names and, by extension, Postgres columns.
    """

    def __init__(self, sqlite_conn: sqlite3.Connection):
        self.conn = sqlite_conn

    def iter_table_rows(self, table_name: str, batch_size: int = 1000) -> Iterator[List[dict]]:

        if table_name not in TABLE_TO_DATACLASS:
            raise ValueError(f"unknown table: {table_name}")

        model_cls = TABLE_TO_DATACLASS[table_name]

        # Use a dedicated cursor for predictable streaming.
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM "{table_name}";')

        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break

            # Validate shape via dataclass constructor.
            batch = [asdict(model_cls(*row)) for row in rows]
            yield batch

    def iter_all_tables(self, tables: Iterable[str], batch_size: int = 1000) -> Iterator[tuple[str, List[dict]]]:
        """Yield table_name, batch pairs for multiple tables."""

        for table in tables:
            for batch in self.iter_table_rows(table, batch_size=batch_size):
                yield table, batch
