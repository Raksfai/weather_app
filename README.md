# Atmos Weather App

Atmos is a Django weather dashboard that shows current weather, a 5-day forecast, interactive charts, animated weather backgrounds, favorites, city comparison, and multilingual UI.

The app uses OpenWeatherMap for weather data and keeps lightweight user state, such as favorites and compared cities, in browser `localStorage`.

## Features

- Search current weather by city.
- Display temperature, feels-like temperature, humidity, pressure, country, description, and weather emoji.
- Show a 5-day forecast from OpenWeatherMap.
- Show an interactive Chart.js graph for temperature and humidity.
- Switch the chart by clicking forecast day cards.
- Change animated page background by selected day weather condition.
- Save favorite cities in `localStorage`.
- Compare up to 5 cities side by side.
- Compare current temperature, humidity, and pressure in separate mini charts.
- Sort comparison table by city, temperature, humidity, or pressure.
- Multilingual interface: English, Ukrainian, Russian, German, Spanish, and Polish.
- Request localized weather descriptions from OpenWeatherMap using the active UI language.

## Tech Stack

- Python 3.12
- Django 6
- SQLite for local development
- OpenWeatherMap API
- Chart.js via CDN
- WhiteNoise for production static files
- `uv` for dependency and command execution
- Ruff for linting

## Project Structure

```text
core/
  settings.py          Django settings, i18n, static files, middleware
  urls.py              Root URL routing
weather/
  views.py             Weather search, forecast processing, compare JSON endpoint
  urls.py              App routes
  tests.py             Django tests with mocked weather API calls
  templates/weather/
    index.html         Main page, modal, translated UI
  static/weather/
    style.css          Layout, weather themes, animations, modal styles
    weather-chart.js   Main forecast chart
    compare.js         Compare localStorage, modal, charts, table
    favorites.js       Favorites localStorage dropdown
locale/
  */LC_MESSAGES/       Translation source and compiled message files
```

## Environment Variables

Create a `.env` file in the project root.

```env
SECRET_KEY=your-django-secret-key
WEATHER_API_KEY=your-openweathermap-api-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

Required variables:

- `SECRET_KEY`: Django secret key.
- `WEATHER_API_KEY`: OpenWeatherMap API key.

Recommended variables:

- `DEBUG`: set `True` for local development and `False` for production.
- `ALLOWED_HOSTS`: comma-separated host list for deployed environments.

## Installation

Install dependencies with the locked dependency set:

```bash
uv sync
```

Apply migrations:

```bash
uv run python manage.py migrate
```

Compile translations after changing `.po` files:

```bash
uv run python manage.py compilemessages
```

## Running Locally

Start the Django development server:

```bash
uv run python manage.py runserver
```

If your environment defaults to `DEBUG=False`, run locally with:

```bash
DEBUG=True uv run python manage.py runserver 127.0.0.1:8000
```

Then open:

```text
http://127.0.0.1:8000/
```

## Usage

1. Enter a city name in the search box.
2. View current weather and the 5-day forecast.
3. Use the chart to inspect temperature and humidity.
4. Click forecast cards to switch chart data and background theme.
5. Click `⭐ Add to favorites` to save the city locally.
6. Click `⚖️ Add to compare` to add the city to the comparison list.
7. Add at least two cities, then click `⚖️ Compare (N)` to open the comparison modal.
8. Use the language selector in the header to switch the UI language.

## Weather Backgrounds

The page theme is based on OpenWeatherMap condition IDs:

- Clear: sunny animated background.
- Clouds: drifting cloud background.
- Rain: falling rain drops.
- Snow: falling snow.
- Thunderstorm: storm clouds, rain, and lightning.
- Mist and fog-like conditions: muted mist background.

When a forecast day is selected, the background switches to that day’s weather theme.

## City Comparison

Compared cities are stored in browser `localStorage` under the `compare` key.

Behavior:

- Maximum 5 cities.
- Re-clicking the compare button toggles the current city in or out.
- The compare modal fetches fresh current weather from `/compare/?cities=...`.
- Failed cities are shown as errors while successful cities still render.
- Three separate charts compare temperature, humidity, and pressure.
- The table can be sorted by city, temperature, humidity, and pressure.

## Favorites

Favorites are stored in browser `localStorage` under the `favorites` key.

The favorites dropdown links back to saved city searches.

## Internationalization

The project uses Django gettext-based i18n.

Supported languages:

- `en`: English
- `uk`: Ukrainian
- `ru`: Russian
- `de`: German
- `es`: Spanish
- `pl`: Polish

Translation files live in:

```text
locale/<language>/LC_MESSAGES/django.po
locale/<language>/LC_MESSAGES/django.mo
```

After editing translations, run:

```bash
uv run python manage.py compilemessages
```

The active language is also passed to OpenWeatherMap as the `lang` parameter so weather descriptions are localized when supported by the API.

JavaScript UI strings are translated through a server-rendered JSON dictionary in the main template.

## Testing

Run the Django test suite:

```bash
uv run python manage.py test
```

Run lint checks:

```bash
uv run ruff check .
```

Current tests cover:

- Successful weather page rendering.
- Current weather plus forecast chart data.
- Forecast grouping by date.
- Error state for unknown city.
- City comparison JSON endpoint.
- Compare deduplication and 5-city limit.
- Partial compare errors.
- i18n rendering and translated JSON errors.
- OpenWeatherMap `lang` parameter usage.

## Static Files

For production static collection:

```bash
uv run python manage.py collectstatic
```

When `DEBUG=False`, WhiteNoise uses `CompressedManifestStaticFilesStorage`, so production deployments must run `collectstatic`.

## Notes

- Do not commit real secrets or API keys.
- External weather requests should be mocked in tests.
- Browser state for favorites and comparison is local to the user’s browser.
- Chart.js is loaded from CDN, so charts require browser network access to that CDN.
