# Django Movies Admin Panel (SQLite → Postgres)

Small educational project: migrate a movies dataset from SQLite to PostgreSQL and manage it via Django Admin.

## Structure
- `schema_design/` — PostgreSQL schema (`postgres_schema.sql`)
- `sqlite_to_postgres/` — migration script (SQLite → Postgres)
- `movies_admin/` — Django Admin panel

## Requirements
- Python 3.9+
- PostgreSQL
- just (task runner)

## Environment

### 1) Create .env in the repo root (copy from .env.template) and set real values:
```bash
DB_NAME='movies'
DB_USER='postgres'
DB_PASSWORD='your_password'
DB_HOST='localhost'
DB_PORT='5432'
SECRET_KEY='your_secret'
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 2) Install dependencies:
```bash
just install
```

### 3) Migrate SQLite -> Postgres (creates content schema/tables if missing):
```bash
just migrate
```

### 4) Run Django Admin:
```bash
just admin-migrate
just superuser
just run
```
### 5) Open:
`http://127.0.0.1:8000/admin/`
