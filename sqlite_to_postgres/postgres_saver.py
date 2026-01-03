import os
import time
import logging
import psycopg2
from psycopg2.extensions import connection as _connection


def measure_time(func):
    def time_it(*args, **kwargs):
        time_started = time.time()
        result = func(*args, **kwargs)
        time_elapsed = time.time()
        values = kwargs.get("values") or []
        logging.info(
            "{execute} running time is {sec} seconds for inserting {rows} rows.".format(
                execute=func.__name__,
                sec=round(time_elapsed - time_started, 4),
                rows=len(values),
            )
        )
        return result

    return time_it


class PostgresSaver:
    def __init__(self, psql_conn: _connection):
        self.connection = psql_conn
        self.cursor = self.connection.cursor()

    def _content_schema_exists(self) -> bool:
        self.cursor.execute("select 1 from pg_tables where schemaname='content' limit 1;")
        return self.cursor.fetchone() is not None

    def create_tables(self):
        base_dir = os.path.dirname(__file__)
        path = os.path.abspath(os.path.join(base_dir, "..", "schema_design", "postgres_schema.sql"))
        with open(path, "r", encoding="utf-8") as f:
            self.cursor.execute(f.read())
        logging.info("schema was created.")
        self.connection.commit()

    def save_all_data(self, data):
        if not self._content_schema_exists():
            self.create_tables()

        for table in data:
            for data_table in data[table]:
                columns_names = list(data_table.keys())

                query = "INSERT into content.{0} ({1}) VALUES ({2}) ON CONFLICT (id) DO NOTHING".format(
                    table,
                    ", ".join(columns_names),
                    ", ".join("%s" for _ in range(len(columns_names))),
                )
                values = tuple(data_table.values())

                try:
                    self.cursor.execute(query, values)
                except psycopg2.Error as error:
                    logging.exception(error)
                    
                    try:
                        if isinstance(error, (psycopg2.errors.UndefinedTable, psycopg2.errors.InvalidSchemaName)):
                            self.create_tables()
                            self.cursor.execute(query, values)
                        else:
                            raise
                    except AttributeError:
                        raise

            logging.info(f"data from {table} was migrated.")

        self.connection.commit()
