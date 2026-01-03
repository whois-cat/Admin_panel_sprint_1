import sqlite3
import logging
from dataclasses import asdict
from db_classes import Genre, Person, FilmWork, GenreFilmWork, PersonFilmWork


class SQLiteLoader:
    def __init__(self, sqlite_cursor):
        self.cursor = sqlite_cursor

    def load_movies(self):
        table_to_class = {
            "genre": Genre,
            "person": Person,
            "film_work": FilmWork,
            "genre_film_work": GenreFilmWork,
            "person_film_work": PersonFilmWork,
        }

        def get_data(table):
            try:
                rows = self.cursor.execute(f'SELECT * FROM "{table}"').fetchall()
            except sqlite3.Error as error:
                logging.exception(error)
                raise

            cls = table_to_class[table]
            data_from_table = [asdict(cls(*row)) for row in rows]
            return data_from_table

        data = {}
        tables = ["genre", "person", "film_work", "genre_film_work", "person_film_work"]
        for table in tables:
            data[table] = get_data(table)

        return data
