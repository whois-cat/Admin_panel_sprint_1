CREATE SCHEMA IF NOT EXISTS content;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    certificate TEXT,
    file_path TEXT,
    rating NUMERIC(2, 1),
    type TEXT NOT NULL,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    birth_date DATE,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    genre_id uuid NOT NULL,
    created_at TIMESTAMPTZ,
    FOREIGN KEY (film_work_id)
        REFERENCES content.film_work(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (genre_id)
        REFERENCES content.genre(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

DO $$
BEGIN
    CREATE TYPE person_role AS ENUM ('actor', 'director', 'writer');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    person_id uuid NOT NULL,
    role TEXT NOT NULL,
    created_at TIMESTAMPTZ,
    UNIQUE (film_work_id, person_id, role),
    FOREIGN KEY (film_work_id)
        REFERENCES content.film_work(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (person_id)
        REFERENCES content.person(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE UNIQUE INDEX film_work_genre ON content.genre_film_work (film_work_id, genre_id);

CREATE UNIQUE INDEX film_work_person_role ON content.person_film_work (film_work_id, person_id, role);
