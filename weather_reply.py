import requests
import json
import math
import datetime
import telebot
from telebot import types

bot = telebot.TeleBot('bot_token')
API = 'your_API'

@bot.message_handler(content_types=['text'])
def weather_report(message):
    """Функция принимает входное значение города, производит запрос к API, олучает информацию и выводит выбранные данные в виде сообщения-ответа"""
    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric&lang=ru')
    if res.status_code == 200:
        data = json.loads(res.text)
        grad = data["name"]
        cur_temp = data["main"]["temp"]
        feel_like_temp = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = datetime.datetime.fromtimestamp(
            data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        code_to_smile = {
            "Clear": "Ясно \U00002600",
            "Clouds": "Облачно \U00002601",
            "Rain": "Дождь \U00002614",
            "Drizzle": "Дождь \U00002614",
            "Thunderstorm": "Гроза \U000026A1",
            "Snow": "Снег \U0001F328",
            "Mist": "Туман \U0001F32B"
        }
        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Неизвестная погода"
        bot.reply_to(message,
                     f"Погода в городе: {grad}\nВремя запроса: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\nТемпература: {cur_temp}°C\nОщущается как: {feel_like_temp}°C\n{wd}\nВлажность: {humidity}%\nДавление: {math.ceil(pressure / 1.333)} мм.рт.ст\nВетер: {wind} м/с \nВосход: {sunrise}\nЗакат: {sunset}\nПродолжительность дня: {length_of_the_day}\n")
    else:
        bot.reply_to(message, 'Город не найден :(')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Выбрать город")
    btn2 = types.KeyboardButton("Назад")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, 'Желаете выбрать новый город?', reply_markup=markup)