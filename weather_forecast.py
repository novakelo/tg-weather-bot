import requests
import json
import matplotlib.pyplot as plt
import telebot
from telebot import types

bot = telebot.TeleBot('bot_token')
API = 'your_API'

@bot.message_handler(content_types=['text'])
def future_weather(message):
    """Функция принимает входное значение города, производит запрос к API, олучает информацию и выводит её в виде графика"""
    city = message.text.strip().lower()
    res = requests.get(
        f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API}&units=metric&lang=ru')
    if res.status_code == 200:
        data = json.loads(res.text)
        forecast_list = data['list']
        temp = [forecast['main']['temp'] for forecast in forecast_list]
        date = [forecast['dt_txt'] for forecast in forecast_list]
        plt.plot(date, temp)
        plt.xticks(rotation=90)
        plt.xlabel('Дата')
        plt.ylabel('Температура')
        plt.title('Прогноз на 5 дней')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('myplot.png')
        plt.show()
        image = 'myplot.png'
        pic = open('./' + image, 'rb')
        bot.send_photo(message.chat.id, pic)
    else:
        bot.reply_to(message, 'Город не найден :(')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Посмотреть прогноз")
    btn2 = types.KeyboardButton("Назад")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, 'Желаете выбрать новый город?', reply_markup=markup)
