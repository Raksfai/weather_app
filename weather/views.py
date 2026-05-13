from collections import defaultdict
from datetime import UTC, datetime, timedelta

import requests
from django.shortcuts import render
from core.settings import WEATHER_API_KEY


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
            "title": f"Weather chart for {format_display_date(date_value)}",
            "theme": get_weather_theme(
                current_weather_id if date_value == current_date else daily_item["weather_id"]
            ),
            "points": points,
        }

    if current_date and current_date not in chart_data:
        chart_data[current_date] = {
            "title": f"Weather chart for {format_display_date(current_date)}",
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
        return render(request, "weather/index.html")

    weather_now = f"https://api.openweathermap.org/data/2.5/weather?q={data}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(weather_now)
    weather_data = response.json()

    if str(weather_data.get("cod")) != "200":
        return render(request, "weather/index.html", {"error": "City wasn't found"})

    weather_id = weather_data["weather"][0]["id"]
    context = {
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

    weather_forecast = f"https://api.openweathermap.org/data/2.5/forecast?q={data}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(weather_forecast)
    forecast_data = response.json()

    forecast_context, chart_data, selected_chart_date = build_forecast_data(
        forecast_data.get("list", []),
        weather_data,
    )
    context["forecast"] = forecast_context
    context["chart_data"] = chart_data
    context["selected_chart_date"] = selected_chart_date
    return render(request, "weather/index.html", context)
