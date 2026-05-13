from datetime import UTC, datetime
from unittest.mock import patch

from django.test import TestCase, override_settings


class MockWeatherResponse:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


def current_weather_payload(weather_id=800):
    return {
        "cod": 200,
        "dt": int(datetime(2026, 5, 14, 9, 30, tzinfo=UTC).timestamp()),
        "timezone": 0,
        "name": "Kyiv",
        "sys": {"country": "UA"},
        "main": {
            "temp": 21.4,
            "feels_like": 22.0,
            "humidity": 61,
            "pressure": 1012,
        },
        "weather": [{"id": weather_id, "description": "clear sky"}],
    }


def forecast_item(date_time, temp, humidity, weather_id=801):
    return {
        "dt_txt": date_time,
        "main": {
            "temp": temp,
            "feels_like": temp + 0.4,
            "humidity": humidity,
            "pressure": 1011,
        },
        "weather": [{"id": weather_id, "description": "few clouds"}],
    }


def forecast_payload():
    return {
        "cod": "200",
        "list": [
            forecast_item("2026-05-14 00:00:00", 9.2, 84),
            forecast_item("2026-05-14 03:00:00", 8.1, 88),
            forecast_item("2026-05-14 12:00:00", 23.1, 58),
            forecast_item("2026-05-14 15:00:00", 24.7, 53),
            forecast_item("2026-05-15 00:00:00", 18.8, 70, 500),
            forecast_item("2026-05-15 03:00:00", 17.6, 74, 500),
            forecast_item("2026-05-15 12:00:00", 22.3, 64, 500),
        ],
    }


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class WeatherIndexTests(TestCase):
    @patch("weather.views.requests.get")
    def test_valid_city_renders_weather_forecast_theme_and_chart_data(self, mock_get):
        mock_get.side_effect = [
            MockWeatherResponse(current_weather_payload()),
            MockWeatherResponse(forecast_payload()),
        ]

        response = self.client.get("/", {"city": "Kyiv"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["city"], "Kyiv")
        self.assertEqual(response.context["weather_emoji"], "☀️")
        self.assertEqual(response.context["weather_theme"], "clear")
        self.assertEqual(response.context["selected_chart_date"], "2026-05-14")
        self.assertContains(response, 'class="forecast-card glass is-active"')
        self.assertContains(response, 'data-date="2026-05-14"')
        self.assertContains(response, 'id="weather-chart-data"')
        self.assertContains(response, "weather-clear")

    @patch("weather.views.requests.get")
    def test_today_chart_includes_current_weather_plus_today_forecast(self, mock_get):
        mock_get.side_effect = [
            MockWeatherResponse(current_weather_payload()),
            MockWeatherResponse(forecast_payload()),
        ]

        response = self.client.get("/", {"city": "Kyiv"})
        points = response.context["chart_data"]["2026-05-14"]["points"]

        self.assertEqual(
            points,
            [
                {"label": "00:00", "temp": 9.2, "humidity": 84},
                {"label": "03:00", "temp": 8.1, "humidity": 88},
                {"label": "09:30", "temp": 21.4, "humidity": 61},
                {"label": "12:00", "temp": 23.1, "humidity": 58},
                {"label": "15:00", "temp": 24.7, "humidity": 53},
            ],
        )

    @patch("weather.views.requests.get")
    def test_future_day_chart_groups_all_returned_forecast_points(self, mock_get):
        mock_get.side_effect = [
            MockWeatherResponse(current_weather_payload()),
            MockWeatherResponse(forecast_payload()),
        ]

        response = self.client.get("/", {"city": "Kyiv"})
        future_points = response.context["chart_data"]["2026-05-15"]["points"]

        self.assertEqual(
            future_points,
            [
                {"label": "00:00", "temp": 18.8, "humidity": 70},
                {"label": "03:00", "temp": 17.6, "humidity": 74},
                {"label": "12:00", "temp": 22.3, "humidity": 64},
            ],
        )
        self.assertEqual(response.context["chart_data"]["2026-05-15"]["theme"], "rain")

    @patch("weather.views.requests.get")
    def test_unknown_city_renders_error_state(self, mock_get):
        mock_get.return_value = MockWeatherResponse({"cod": "404"})

        response = self.client.get("/", {"city": "Missing"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["error"], "City wasn't found")
        self.assertContains(response, "City wasn&#x27;t found")
        self.assertEqual(mock_get.call_count, 1)
