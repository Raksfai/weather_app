import requests
from django.shortcuts import render
from core.settings import WEATHER_API_KEY

def index(request):
    data = request.GET.get("city")
    if not data:
        return render(request, "weather/index.html")
    print("User input:", data)
    req = f"https://api.openweathermap.org/data/2.5/weather?q={data}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(req)
    weather_data = response.json()
    if weather_data.get("cod") != 200:
        print("Error: 404", weather_data.get("cod"))
        return render(request, "weather/index.html", {"error":"City wasn't found"})
    context = {
        'country': weather_data['sys']['country'],
        'city': weather_data['name'],
        'temp': weather_data['main']['temp'],
        'feels_like': weather_data['main']['feels_like'],
        'humidity': weather_data['main']['humidity'],
        'pressure': weather_data['main']['pressure'],
        'description': weather_data['weather'][0]['description'],
    }
    print("\n(TEST)Main weather data:", context.get("main", {}))
    return render(request, "weather/index.html", context)
