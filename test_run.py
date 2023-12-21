import unittest
from unittest.mock import MagicMock
from weatherbot import run_bot

class TestRunBot(unittest.TestCase):
    def test_run_bot(self):
        mock_infinity_polling = MagicMock()
        original_infinity_polling = bot.infinity_polling
        bot.infinity_polling = mock_infinity_polling

        run_bot()

        mock_infinity_polling.assert_called_once()

        bot.infinity_polling = original_infinity_polling

if __name__ == '__main__':
    unittest.main()