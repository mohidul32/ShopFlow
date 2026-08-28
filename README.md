# ShopFlow

ShopFlow is a production-oriented Django REST API for a multi-seller e-commerce
marketplace. Its design decisions are documented in
[`docs/step-01-requirements-architecture.md`](docs/step-01-requirements-architecture.md).

## Local development

Prerequisites: Python 3.11+ and PostgreSQL 16+.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
cp .env.example .env
createuser -P shopflow
createdb -O shopflow shopflow
python manage.py migrate
python manage.py runserver
```

The liveness endpoint is available at `http://127.0.0.1:8000/api/v1/health/live/`.

`DATABASE_URL` must be a PostgreSQL URL, for example:

```text
postgresql://shopflow:shopflow@127.0.0.1:5432/shopflow
```

## Settings

Development uses `config.settings.development`. Production uses
`config.settings.production` and requires a real `DJANGO_SECRET_KEY` and
`DJANGO_ALLOWED_HOSTS`. Never commit `.env` files.

## Quality checks

```bash
ruff check .
pytest
python manage.py check
```
