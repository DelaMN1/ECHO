# ECHO

ECHO is a Flask blog application rebuilt around a proper application package, SQLAlchemy models, service-backed route handlers, and isolated integration tests.

## What Changed

The old version mixed routes, raw SQLite access, form validation queries, and session handling directly in feature modules. The rebuilt version separates those concerns:

- `echo_app/` contains the application package
- `echo_app/extensions.py` initializes shared Flask extensions
- `echo_app/models.py` defines the SQLAlchemy data model
- `echo_app/auth/` handles registration, login, and logout
- `echo_app/blog/` handles post creation, editing, search, tagging, digest views, and version history
- `tests/` exercises the rebuilt app with an isolated database per test run

## Stack

- Flask
- Flask-WTF
- Flask-Bcrypt
- Flask-SQLAlchemy
- SQLite by default

## Project Layout

```text
ECHO/
├── app.py
├── echo_app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models.py
│   ├── auth/
│   ├── blog/
│   └── utils/
├── templates/
├── static/
├── tests/
├── requirements.txt
└── .env.example
```

## Features

- User registration and login
- Session-based authentication
- Create, edit, and delete posts
- Owner-only post editing and deletion
- Version history for edited posts
- Search across titles, content, summaries, and tags
- Tag pages and weekly digest view
- Reading-time and summary generation

## Local Setup

1. Create a virtual environment and install dependencies.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Create a local environment file.

```bash
copy .env.example .env
```

3. Start the app.

```bash
python app.py
```

The app will create its SQLite database automatically under `instance/` when it starts.

## Configuration

Supported environment variables:

- `FLASK_ENV`
- `SECRET_KEY`
- `DATABASE_URL`
- `POSTS_PER_PAGE`

Default local database:

- `instance/echo.db`

## Testing

Run the suite with:

```bash
pytest tests -q
```

The tests use an isolated temporary database and do not touch the local development database.

## Deployment

`gunicorn app:app` remains the production entrypoint, so existing Render and Procfile wiring can stay in place.
