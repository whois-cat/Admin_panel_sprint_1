from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List, Sequence

from psycopg2 import sql
from psycopg2.extensions import connection as _connection
from psycopg2.extras import execute_values


logger = logging.getLogger(__name__)


class PostgresSaver:
    """Writes batches of rows into Postgres."""

    def __init__(self, psql_conn: _connection):
        self.connection = psql_conn
        self.cursor = self.connection.cursor()

    def ensure_schema(self) -> None:
        """Create tables if they do not exist."""

        repo_root = Path(__file__).resolve().parents[1]
        schema_path = repo_root / "schema_design" / "postgres_schema.sql"

        schema_sql = schema_path.read_text(encoding="utf-8")

        self.cursor.execute(schema_sql)
        self.connection.commit()
        logger.info("Schema ensured (schema_design/postgres_schema.sql).")

    def insert_batch(self, table: str, rows: List[dict], page_size: int = 1000) -> int:
        """Insert one batch into content.<table>."""

        if not rows:
            return 0

        columns: Sequence[str] = list(rows[0].keys())
        values: List[tuple] = [tuple(row[col] for col in columns) for row in rows]

        query = sql.SQL(
            "INSERT INTO content.{table} ({cols}) VALUES %s ON CONFLICT (id) DO NOTHING"
        ).format(
            table=sql.Identifier(table),
            cols=sql.SQL(", ").join(sql.Identifier(c) for c in columns),
        )

        execute_values(
            self.cursor,
            query.as_string(self.cursor),
            values,
            page_size=page_size,
        )
        return len(values)

    def save_table_stream(self, table: str, batches: Iterable[List[dict]], batch_size: int = 1000) -> None:
        """Save a stream of batches for a given table."""

        total = 0
        for batch in batches:
            total += self.insert_batch(table, batch, page_size=batch_size)

        self.connection.commit()
        logger.info("Migrated table %s (processed %d rows).", table, total)
