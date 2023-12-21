import telebot
from telebot import types
import requests
import json
import math
import datetime
import matplotlib.pyplot as plt
import threading

bot = telebot.TeleBot('bot_token')
API = 'your_API'

monitoring_settings = {}

@bot.message_handler(commands=['start'])
def main(message: str):
    """Функция выводит в чат кнопки"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Отчёт о погоде")
    btn2 = types.KeyboardButton("Прогноз на 5 дней")
    btn3 = types.KeyboardButton("Мониторинг")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, 'Здравствуйте, выберите выполняемую функцию:', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def func(message: str):
    """Функция хранит все возможные варианты команд и реакции на них"""
    catch = message.text.strip().lower()
    if catch == 'отчёт о погоде':
        bot.send_message(message.chat.id, 'Введите название города для отчёта:')
        bot.register_next_step_handler(message, weather_report)

    elif catch == 'прогноз на 5 дней':
        bot.send_message(message.chat.id, 'Введите название города для прогноза:')
        bot.register_next_step_handler(message, future_weather)

    elif catch == 'мониторинг':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Выбрать город мониторинга")
        btn2 = types.KeyboardButton("Отключить мониторинг")
        btn3 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, 'Выберите опцию мониторинга:', reply_markup=markup)

    elif catch == 'назад':
        bot.send_message(message.chat.id, 'Возвращаемся в главное меню...')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Отчёт о погоде")
        btn2 = types.KeyboardButton("Прогноз на 5 дней")
        btn3 = types.KeyboardButton("Мониторинг")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, 'Выберите выполняемую функцию:', reply_markup=markup)

    elif catch == "выбрать город мониторинга":
        bot.send_message(message.chat.id, 'Введите название города для мониторинга:')
        bot.register_next_step_handler(message, set_monitoring_city)

    elif catch == 'посмотреть прогноз':
        bot.send_message(message.chat.id, 'Введите название города:')
        bot.register_next_step_handler(message, future_weather)

    elif catch == 'выбрать город':
        bot.send_message(message.chat.id, 'Введите название города:')
        bot.register_next_step_handler(message, weather_report)

    elif catch == 'отключить мониторинг':
        chat_id = message.chat.id
        if chat_id in monitoring_settings:
            monitoring_settings.pop(chat_id)
            bot.send_message(chat_id, 'Мониторинг отключен')
        else:
            bot.send_message(chat_id, 'Мониторинг не настроен')

    else:
        bot.send_message(message.chat.id, 'Введите команду из предложенного списка, я Вас не понимаю :(')



@bot.message_handler(func=lambda message: message.content_type == 'text' and message.chat.id in monitoring_settings.keys())
def monitoring_min_wind_speed(message: str):
    """Функция для выбора скорости и установки мониторинга"""
    chat_id = message.chat.id
    speed = message.text.strip()
    try:
        speed = float(speed)
        monitoring_settings[chat_id]['min_wind_speed'] = speed
        monitoring_settings[chat_id]['current_wind_speed'] = 0
        monitoring_settings[chat_id]['notification_enabled'] = True
        bot.send_message(chat_id, 'Мониторинг настроен успешно!')
        start_monitoring(chat_id)
    except ValueError:
        bot.send_message(chat_id, 'Некорректная скорость ветра. Попробуйте еще раз.')
        bot.register_next_step_handler(message, monitoring_min_wind_speed)


def set_monitoring_city(message: str):
    """Функция выбора города мониторинга"""
    chat_id = message.chat.id
    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric&lang=ru')
    if res.status_code == 200:
        monitoring_settings[chat_id] = {'city': city}
        bot.send_message(chat_id, 'Мониторинг включен')
        bot.send_message(chat_id, 'Введите скорость ветра (м/с), при превышении которой желаете получать уведомления: ')
        bot.register_next_step_handler(message, monitoring_min_wind_speed)
    else:
        bot.reply_to(message, 'Город не найден :(')
        bot.send_message(message.chat.id, 'Желаете выбрать новый город?')

@bot.message_handler(content_types=['text'])
def weather_report(message: str):
    """Функция составляет и выводит на экран небольшой отчёт о погоде"""
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
@bot.message_handler(content_types=['text'])
def future_weather(message: str):
    """Функция выводит график прогноза погоды"""
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

def start_monitoring(chat_id: int):
    threading.Timer(5, check_wind_speed, args=[chat_id]).start()

def check_wind_speed(chat_id: int):
    if chat_id in monitoring_settings:
        city = monitoring_settings[chat_id]['city']
        res = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric&lang=ru')
        if res.status_code == 200:
            data = json.loads(res.text)
            current_wind_speed = data['wind']['speed']
            monitoring_settings[chat_id]['current_wind_speed'] = current_wind_speed
            min_wind_speed = monitoring_settings[chat_id]['min_wind_speed']
            if current_wind_speed >= min_wind_speed and monitoring_settings[chat_id]['notification_enabled']:
                bot.send_message(chat_id, f'Скорость ветра в городе {city} превысила {min_wind_speed} м/с!\n'
                                          f'Текущая скорость ветра: {current_wind_speed} м/с.')
            start_monitoring(chat_id)

def run_bot():
    bot.infinity_polling()