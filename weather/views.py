from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django.utils.translation import override
from core.settings import WEATHER_API_KEY


COMPARE_LIMIT = 5
OPENWEATHER_LANGUAGES = {"en", "uk", "ru", "de", "es", "pl"}


def get_openweather_language(language_code=None):
    language = (language_code or get_language() or "en").split("-")[0]
    return language if language in OPENWEATHER_LANGUAGES else "en"


def get_js_i18n():
    return {
        "addAtLeastTwo": _("Add at least two cities to compare."),
        "addToCompare": _("⚖️ Add to compare"),
        "city": _("City"),
        "cityComparison": _("City comparison"),
        "closeCompareModal": _("Close compare modal"),
        "compare": _("Compare"),
        "comparisonUnavailable": _("Comparison is unavailable."),
        "favorites": _("Favorites"),
        "humidity": _("Humidity"),
        "inCompare": _("✓ In compare"),
        "loadingComparison": _("Loading comparison..."),
        "maximumCities": _("Maximum 5 cities. Remove one to add another."),
        "noFavorites": _("No favorites yet."),
        "pressure": _("Pressure"),
        "remove": _("Remove"),
        "selected": _("selected"),
        "selectAtLeastTwo": _("Select at least two cities"),
        "temperature": _("Temperature"),
        "weather": _("Weather"),
    }


def build_base_context():
    return {"i18n": get_js_i18n()}


def get_weather_theme(weather_id):
    """Return a CSS theme key for an OpenWeatherMap condition ID."""
    if weather_id < 300:
        return "thunderstorm"
    if weather_id < 600:
        return "rain"
    if weather_id < 700:
        return "snow"
    if weather_id < 800:
        return "mist"
    if weather_id == 800:
        return "clear"
    return "clouds"


def get_weather_emoji(weather_id):
    """Return an emoji based on the weather condition ID from OpenWeatherMap API."""
    if weather_id < 300:
        return "⛈️"  # гроза
    if weather_id < 400:
        return "🌧️"  # моросить
    if weather_id < 600:
        return "🌧️"  # дощ
    if weather_id < 700:
        return "❄️"  # сніг
    if weather_id < 800:
        return "🌫️"  # туман
    if weather_id == 800:
        return "☀️"  # ясно
    if weather_id < 803:
        return "⛅️"  # невелика хмарність
    return "☁️"  # хмарно


def parse_compare_cities(raw_cities):
    cities = []
    seen = set()
    for city in raw_cities.split(","):
        normalized_city = city.strip()
        city_key = normalized_city.casefold()
        if normalized_city and city_key not in seen:
            cities.append(normalized_city)
            seen.add(city_key)
        if len(cities) == COMPARE_LIMIT:
            break
    return cities


def build_current_weather_context(weather_data):
    weather_id = weather_data["weather"][0]["id"]
    return {
        "name": weather_data["name"],
        "country": weather_data["sys"]["country"],
        "temp": weather_data["main"]["temp"],
        "feels_like": weather_data["main"]["feels_like"],
        "humidity": weather_data["main"]["humidity"],
        "pressure": weather_data["main"]["pressure"],
        "description": weather_data["weather"][0]["description"],
        "emoji": get_weather_emoji(weather_id),
        "theme": get_weather_theme(weather_id),
    }


def fetch_compare_city(city, language_code=None):
    openweather_language = get_openweather_language(language_code)
    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": city,
                "appid": WEATHER_API_KEY,
                "units": "metric",
                "lang": openweather_language,
            },
            timeout=10,
        )
        weather_data = response.json()
    except requests.RequestException:
        with override(openweather_language):
            return {"city": city, "message": _("Weather service is unavailable")}

    if str(weather_data.get("cod")) != "200":
        with override(openweather_language):
            return {"city": city, "message": _("City wasn't found")}

    return build_current_weather_context(weather_data)


def get_local_datetime(timestamp, timezone_offset):
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, UTC) + timedelta(seconds=timezone_offset or 0)


def format_display_date(date_value):
    date = datetime.strptime(date_value, "%Y-%m-%d").date()
    return date.strftime("%d.%m")


def build_chart_point(label, temp, humidity):
    return {
        "label": label,
        "temp": round(float(temp), 1),
        "humidity": int(humidity),
    }


def get_time_sort_value(point):
    hour, minute = point["label"].split(":")
    return int(hour) * 60 + int(minute)


def get_daily_display_item(items):
    return next(
        (item for item in items if item["label"] == "12:00"),
        items[len(items) // 2],
    )


def build_forecast_data(forecast_items, weather_data):
    forecast_by_date = defaultdict(list)

    for item in forecast_items:
        date_value, time_value = item["dt_txt"].split(" ")
        forecast_by_date[date_value].append(
            {
                "label": time_value[:5],
                "temp": item["main"]["temp"],
                "feels_like": item["main"]["feels_like"],
                "humidity": item["main"]["humidity"],
                "pressure": item["main"]["pressure"],
                "description": item["weather"][0]["description"],
                "weather_id": item["weather"][0]["id"],
            }
        )

    local_now = get_local_datetime(weather_data.get("dt"), weather_data.get("timezone"))
    current_date = local_now.strftime("%Y-%m-%d") if local_now else None
    current_label = local_now.strftime("%H:%M") if local_now else "Now"
    current_point = build_chart_point(
        current_label,
        weather_data["main"]["temp"],
        weather_data["main"]["humidity"],
    )
    current_weather_id = weather_data["weather"][0]["id"]

    chart_data = {}
    for date_value, items in forecast_by_date.items():
        daily_item = get_daily_display_item(items)
        points = [
            build_chart_point(item["label"], item["temp"], item["humidity"])
            for item in items
        ]
        if date_value == current_date:
            points.insert(0, current_point)
        points.sort(key=get_time_sort_value)
        chart_data[date_value] = {
            "title": _("Weather chart for %(date)s")
            % {"date": format_display_date(date_value)},
            "theme": get_weather_theme(
                current_weather_id if date_value == current_date else daily_item["weather_id"]
            ),
            "points": points,
        }

    if current_date and current_date not in chart_data:
        chart_data[current_date] = {
            "title": _("Weather chart for %(date)s")
            % {"date": format_display_date(current_date)},
            "theme": get_weather_theme(current_weather_id),
            "points": [current_point],
        }

    forecast_context = []
    for date_value, items in list(forecast_by_date.items())[:5]:
        daily_item = get_daily_display_item(items)
        forecast_context.append(
            {
                "date": format_display_date(date_value),
                "date_key": date_value,
                "temp": daily_item["temp"],
                "feels_like": daily_item["feels_like"],
                "humidity": daily_item["humidity"],
                "pressure": daily_item["pressure"],
                "description": daily_item["description"],
                "emoji": get_weather_emoji(daily_item["weather_id"]),
            }
        )

    selected_chart_date = current_date or next(iter(chart_data), "")
    return forecast_context, chart_data, selected_chart_date


def index(request):
    data = request.GET.get("city")
    if not data:
        return render(request, "weather/index.html", build_base_context())

    weather_now = "https://api.openweathermap.org/data/2.5/weather"
    response = requests.get(
        weather_now,
        params={
            "q": data,
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang": get_openweather_language(),
        },
    )
    weather_data = response.json()

    if str(weather_data.get("cod")) != "200":
        return render(
            request,
            "weather/index.html",
            build_base_context() | {"error": _("City wasn't found")},
        )

    weather_id = weather_data["weather"][0]["id"]
    context = build_base_context() | {
        "country": weather_data["sys"]["country"],
        "city": weather_data["name"],
        "temp": weather_data["main"]["temp"],
        "feels_like": weather_data["main"]["feels_like"],
        "humidity": weather_data["main"]["humidity"],
        "pressure": weather_data["main"]["pressure"],
        "description": weather_data["weather"][0]["description"],
        "weather_emoji": get_weather_emoji(weather_id),
        "weather_theme": get_weather_theme(weather_id),
    }

    weather_forecast = "https://api.openweathermap.org/data/2.5/forecast"
    response = requests.get(
        weather_forecast,
        params={
            "q": data,
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang": get_openweather_language(),
        },
    )
    forecast_data = response.json()

    forecast_context, chart_data, selected_chart_date = build_forecast_data(
        forecast_data.get("list", []),
        weather_data,
    )
    context["forecast"] = forecast_context
    context["chart_data"] = chart_data
    context["selected_chart_date"] = selected_chart_date
    return render(request, "weather/index.html", context)


def compare(request):
    cities = parse_compare_cities(request.GET.get("cities", ""))
    if not cities:
        return JsonResponse({"error": _("No cities provided")}, status=400)

    language_code = get_openweather_language()
    with ThreadPoolExecutor(max_workers=min(len(cities), COMPARE_LIMIT)) as executor:
        results = list(
            executor.map(
                lambda city: fetch_compare_city(city, language_code),
                cities,
            )
        )

    city_results = []
    errors = []
    for result in results:
        if "message" in result:
            errors.append(result)
        else:
            city_results.append(result)

    return JsonResponse({"cities": city_results, "errors": errors})
