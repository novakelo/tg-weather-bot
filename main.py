import telebot
from telebot import types
import requests
import json
import threading

bot = telebot.TeleBot('6437774582:AAEuxPT2j7Jt9llXKybvxC3lTmTXYuK3SvI')
API = 'cb7c19e567c351967e0c8a47f3fa111b'

monitoring_settings = {}

@bot.message_handler(commands=['start'])
def start(message):
    """Функция обрабатывает команду /start и выводит кнопки на экран"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Отчёт о погоде")
    btn2 = types.KeyboardButton("Прогноз на 5 дней")
    btn3 = types.KeyboardButton("Мониторинг")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, 'Здравствуйте, выберите выполняемую функцию:', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    """Функция отвечает за все вводимые команды и их действие"""
    catch = message.text.strip().lower()
    if catch == 'отчёт о погоде':
        bot.send_message(message.chat.id, 'Введите название города для отчёта:')
        from weather_reply import weather_report
        bot.register_next_step_handler(message, weather_report)

    elif catch == 'прогноз на 5 дней':
        bot.send_message(message.chat.id, 'Введите название города для прогноза:')
        from weather_forecast import future_weather
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
        from weather_forecast import future_weather
        bot.register_next_step_handler(message, future_weather)

    elif catch == 'выбрать город':
        bot.send_message(message.chat.id, 'Введите название города:')
        from weather_reply import weather_report
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
def monitoring_min_wind_speed(message):
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


def set_monitoring_city(message):
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


def start_monitoring(chat_id):
    threading.Timer(5, check_wind_speed, args=[chat_id]).start()


def check_wind_speed(chat_id):
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
                bot.send_message(chat_id, f'Скорость ветра в городе {city} превысила {min_wind_speed} м/с!\n'f'Текущая скорость ветра: {current_wind_speed} м/с.')
            start_monitoring(chat_id)


bot.infinity_polling()