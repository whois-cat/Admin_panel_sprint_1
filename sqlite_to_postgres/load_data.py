import os
import time
import sqlite3
import uuid
import datetime
import psycopg2
import getpass
import argparse
from dataclasses import dataclass, astuple


@dataclass
class Genre:
    id: uuid.UUID
    name: str
    description: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class FilmWork:
    id: uuid.UUID
    title: str
    description: str
    creation_date: datetime.date
    certificate: str
    file_path: str
    rating: float
    type: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class Person:
    id: uuid.UUID
    full_name: str
    birth_date: datetime.date
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class GenreFilmWork:
    id: uuid.UUID
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created_at: datetime.datetime


@dataclass
class PersonFilmWork:
    id: uuid.UUID
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    created_at: datetime.datetime


class MigrateData:
    def __init__(self, sqlite, psql, count):
        self.sqlite = sqlite
        self.psql = psql
        self.count = count

    def assert_of_path(self):
        assert os.path.exists(
            self.sqlite
        ), f"File was not found by the path {self.sqlite}"
        assert os.path.exists(self.psql), f"File was not found by the path {self.psql}"

    def connect_psql(self):
        passwd = getpass.getpass("Enter your password: ")
        dsn = {
            "dbname": "movies",
            "user": "postgres",
            "password": f"{passwd}",
            "host": "127.0.0.1",
            "port": 5432,
            'options': '-c search_path=content'
        }
        self.psql_connection = psycopg2.connect(**dsn)
        self.psql_cursor = self.psql_connection.cursor()

    def connect_sqlite(self):
        self.sqlite_connection = sqlite3.connect(f"{self.sqlite}")
        self.sqlite_cursor = self.sqlite_connection.cursor()

    def create_tables(self):
        self.psql_cursor.execute(open(f"{self.psql}", "r").read())
        print('Schema was created.')
        self.psql_connection.commit()

    def get_tables_name(self):
        self.psql_cursor.execute(
            "select * from pg_tables where schemaname='content';"
        )
        if bool(self.psql_cursor.rowcount) is False:
            MigrateData.create_tables(self)
        self.psql_cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='content'"
        )
        tables = [i[0] for i in self.psql_cursor.fetchall()]
        return tables

    def migrate_data(self):
        try:
            for table in MigrateData.get_tables_name(self):
                self.sqlite_cursor.execute(f"SELECT * FROM {table};")
                column_names = [description[0] for description in self.sqlite_cursor.description]
                self.psql_cursor.execute(f"TRUNCATE content.{table} CASCADE;")
                while True:
                    rows = self.sqlite_cursor.fetchmany(int(self.count))
                    if not rows:
                        break
                    data = [astuple(eval(
                                "{}(*row)".format(
                                    "".join(word.capitalize() for word in table.split("_"))
                                )))
                                for row in rows
                    ]
                    time_started = time.time()
                    self.psql_cursor.executemany(
                        "INSERT into content.{0} ({1}) VALUES ({2})".format(
                            table,
                            ", ".join(column_names),
                            ", ".join("%s" for _ in range(len(column_names))),
                        ), data)
                    time_elapsed = time.time()
                    self.psql_connection.commit()
                print("Data from table {} has been migrated by the {}.".format(
                    table, round((time_elapsed - time_started), 4))
                )
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sqlite", required=True, help="The path to sqlite DB.", )
    parser.add_argument("-p", "--psql", required=True, help="The path to sql file with postgres schema.", )
    parser.add_argument("-c", "--count", default=10, help="Count of string for insert.", )
    args = parser.parse_args()
    migration = MigrateData(args.sqlite, args.psql, args.count)
    migration.connect_psql()
    migration.connect_sqlite()
    migration.migrate_data()


if __name__ == "__main__":
    main()