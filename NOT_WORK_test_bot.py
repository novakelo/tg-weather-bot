import unittest
from unittest.mock import patch, Mock
from weather_reply import weather_report

class TestWeatherReport(unittest.TestCase):
    @patch('weather_reply.requests.get')
    def test_weather_report_success(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "Москва",
            "main": {
                "temp": 10,
                "feels_like": 8,
                "humidity": 70,
                "pressure": 1013,
            },
            "wind": {
                "speed": 3.5
            },
            "sys": {
                "sunrise": 1634541078,
                "sunset": 1634579422
            },
            "weather": [{
                "main": "Clouds"
            }]
        }

        expected_reply = ("Погода в городе: Москва\n"
                          "Температура: 10°C\n"
                          "Ощущается как: 8°C\n"
                          "Облачно ☁\n"
                          "Влажность: 70%\n"
                          "Давление: 760 мм.рт.ст\n"
                          "Ветер: 3.5 м/с\n"
                          "Восход: 2021-10-18 05:24:38\n"
                          "Закат: 2021-10-18 16:43:42")

if __name__ == '__main__':
    unittest.main()