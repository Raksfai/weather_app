import requests
from django.shortcuts import render
from core.settings import WEATHER_API_KEY


def get_weather_emoji(weather_id):
    if weather_id < 300:
        return "⛈️"  # гроза
    elif weather_id < 400:
        return "🌧️"  # моросить
    elif weather_id < 600:
        return "🌧️"  # дощ
    elif weather_id < 700:
        return "❄️"  # сніг
    elif weather_id < 800:
        return "🌫️"  # туман
    elif weather_id == 800:
        return "☀️"  # ясно
    elif weather_id < 803:
        return "⛅️"  # невелика хмарність
    else:
        return "☁️"  # хмарно


def index(request):
    data = request.GET.get("city")
    if not data:
        return render(request, "weather/index.html")

    print("User input:", data)
    weather_now = f"https://api.openweathermap.org/data/2.5/weather?q={data}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(weather_now)
    weather_data = response.json()

    if weather_data.get("cod") != 200:
        print("Error: 404", weather_data.get("cod"))
        return render(request, "weather/index.html", {"error": "City wasn't found"})
    context = {
        "country": weather_data["sys"]["country"],
        "city": weather_data["name"],
        "temp": weather_data["main"]["temp"],
        "feels_like": weather_data["main"]["feels_like"],
        "humidity": weather_data["main"]["humidity"],
        "pressure": weather_data["main"]["pressure"],
        "description": weather_data["weather"][0]["description"],
    }
    print("\n(TEST)Main weather data:", context.get("main", {}))

    ####################

    weather_forecast = f"https://api.openweathermap.org/data/2.5/forecast?q={data}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(weather_forecast)
    forecast_data = response.json()
    print("\n(TEST)Forecast data:", forecast_data)
    filtered_forecast = [
        item for item in forecast_data["list"] if item["dt_txt"].endswith("12:00:00")
    ]

    print("\n(TEST)Filtered forecast data:", filtered_forecast)

    forecast_context = []

    for item in filtered_forecast:
        forecast_context.append(
            {
                "date": item["dt_txt"].split(" ")[0].split("-")[2]
                + "."
                + item["dt_txt"].split(" ")[0].split("-")[1],
                "temp": item["main"]["temp"],
                "feels_like": item["main"]["feels_like"],
                "humidity": item["main"]["humidity"],
                "pressure": item["main"]["pressure"],
                "description": item["weather"][0]["description"],
            }
        )

    context["forecast"] = forecast_context
    return render(request, "weather/index.html", context)
