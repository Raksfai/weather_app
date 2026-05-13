# Repository Guidelines

## Project Structure & Module Organization

This is a Django weather application. The Django project configuration lives in `core/`, including `settings.py`, URL routing, ASGI, and WSGI entry points. The main app is `weather/`: views are in `weather/views.py`, app URLs in `weather/urls.py`, templates in `weather/templates/weather/`, and static assets in `weather/static/weather/`. Tests currently belong in `weather/tests.py`; add more test modules under `weather/` if the suite grows. Local SQLite data is stored in `db.sqlite3`.

## Build, Test, and Development Commands

Use `uv` to run project commands with the locked dependency set.

- `uv run python manage.py runserver` starts the local Django development server.
- `uv run python manage.py test` runs the Django test suite.
- `uv run python manage.py migrate` applies database migrations.
- `uv run python manage.py collectstatic` gathers static files for WhiteNoise/production serving.
- `uv run ruff check .` runs Python lint checks.

## Coding Style & Naming Conventions

Target Python 3.12 and Django 6 conventions. Use 4-space indentation, clear snake_case names for Python functions and variables, and PascalCase for classes. Keep view logic readable and extract helpers when API parsing or formatting becomes reused. Django templates should stay under the app template namespace, for example `weather/templates/weather/index.html`. Static files should be named by purpose, such as `style.css` and `favorites.js`.

## Testing Guidelines

Use Django’s built-in test runner. Place tests near the app code in `weather/tests.py` or split into `test_*.py` modules as coverage expands. Name test methods with `test_` and focus on observable behavior: URL responses, context data, error handling, and API parsing. Mock external OpenWeatherMap requests instead of calling the live API during tests.

## Commit & Pull Request Guidelines

Recent commits use short imperative subjects and occasional Conventional Commit prefixes, for example `Fix static files with whitenoise`, `chore(config): add STATIC_ROOT`, and `build(deps): add gunicorn as production server`. Keep commits focused and describe the user-visible or operational effect.

Pull requests should include a concise summary, test results, linked issues when relevant, and screenshots for UI/template or CSS changes. Note any configuration or migration steps reviewers must run.

## Security & Configuration Tips

Configuration is loaded from environment variables via `python-dotenv`. Do not commit real secrets. Required values include `SECRET_KEY`, `WEATHER_API_KEY`, and, for deployed environments, `ALLOWED_HOSTS`.
