import unittest
from unittest.mock import patch, Mock
from weather_reply import weather_report, bot

class TestWeatherReport(unittest.TestCase):
    @patch('weather_reply.requests.get')
    def test_weather_report_success(self, mock_get):
        expected_reply = ("Погода в городе: Moscow\n"
                          "Время запроса: 2023-12-21 23:12\n"
                          "Температура: 10°C\n"
                          "Ощущается как: 8°C\n"
                          "Облачно ☁\n"
                          "Влажность: 70%\n"
                          "Давление: 760 мм.рт.ст\n"
                          "Ветер: 3.5 м/с \n"
                          "Восход: 2021-10-18 10:11:18\n"
                          "Закат: 2021-10-18 20:50:22\n"
                          "Продолжительность дня: 10:39:04\n")

        # Остальной код не изменяется
        message = Mock()
        message.text = 'Москва'
        message.chat.id = 764211713  # Замените на актуальный идентификатор чата
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"name": "Moscow", "main": {"temp": 10, "feels_like": 8, "humidity": 70, "pressure": 1013}, "wind": {"speed": 3.5}, "sys": {"sunrise": 1634541078, "sunset": 1634579422}, "weather": [{"main": "Clouds"}]}'

        mock_get.return_value = mock_response
        
        with patch.object(bot, 'reply_to') as mock_reply_to:
            weather_report(message)
            mock_reply_to.assert_called_once_with(764211713, expected_reply)  # Изменен вызов для подходящих аргументов

if __name__ == '__main__':
    unittest.main()