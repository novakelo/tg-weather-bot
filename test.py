import unittest
from unittest.mock import patch
from weatherbot import run_bot

class TestRunBot(unittest.TestCase):
    @patch('weatherbot.bot.infinity_polling')

    def test_run_bot(self, mock_infinity_polling):
        run_bot()
        mock_infinity_polling.assert_called_once()

if __name__ == '__main__':
    unittest.main()