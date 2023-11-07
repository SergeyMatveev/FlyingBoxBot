import logging

from telegram.ext import ConversationHandler
from constants import MAX_ATTEMPTS
from database import insert_request_into_database
from datetime import datetime, date
import re
from dateutil.relativedelta import relativedelta
import json

CITY_FROM, CITY_TO, WEIGHT, SEND_DATE, WHAT_IS_INSIDE = range(5)

# Загрузка JSON-файла со списком городов
with open('cities.json', 'r', encoding='utf-8') as f:
    cities_data = json.load(f)


def parse_weight(weight_str):
    weight_str = weight_str.replace(',', '.')
    match = re.search(r'(\d+(\.\d+)?)', weight_str)
    if match:
        return float(match.group(1))
    else:
        return None


# Функция для проверки существования города
def check_city_exists(city_name):
    for city in cities_data['city']:
        if city['name'].lower() == city_name.lower():
            return True
    return False


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def send_package(update, context):
    logging.info(f"User {update.message.from_user.username} entered send_package function.")

    if 'conversation' in context.user_data:
        logging.info(f"Error. User {update.message.from_user.username} tried to start new process without finishing previous.")
        update.message.reply_text(f"Вы уже находитесь в процессе создания заказа.\nЗакончите его или нажмите /cancel")
        return ConversationHandler.END
    context.user_data['conversation'] = True

    try:
        update.message.reply_text(f"Вы находитесь в процессе создания нового заказа.\n"
                                  f"Закончите его или отправьте /cancel для отмены.\n\n"
                                  f"Шаг 1/5. Введите город отправления посылки:\n")
        logging.info("Sent request for country of origin.")

        context.user_data['country_from_attempts'] = 0
        context.user_data['country_to_attempts'] = 0
        context.user_data['city_from_attempts'] = 0
        context.user_data['city_to_attempts'] = 0
        context.user_data['date_attempts'] = 0

        logging.info("Initialized user data for attempts.")

        return CITY_FROM

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return ConversationHandler.END  # Or some other state indicating an error


def city_from(update, context):

    user_city = update.message.text.lower()
    attempts = context.user_data.get('city_from_attempts', 0) + 1
    context.user_data['city_from_attempts'] = attempts

    if check_city_exists(user_city):
        context.user_data['city_from'] = user_city
        context.user_data['city_from_attempts'] = 0
        update.message.reply_text("Шаг 2/5. Введите город назначения:")
        return CITY_TO
    else:
        if attempts >= MAX_ATTEMPTS:
            update.message.reply_text("Вы ввели город неправильно 5 раз. Попробуйте оформить заявку снова.")
            return ConversationHandler.END
        else:
            update.message.reply_text("Я не знаю такого города, попробуйте ввести по-другому.")
            return CITY_FROM


def city_to(update, context):
    user_city = update.message.text.lower()
    attempts = context.user_data.get('city_to_attempts', 0) + 1
    context.user_data['city_to_attempts'] = attempts

    if check_city_exists(user_city):
        context.user_data['city_to'] = user_city
        context.user_data['city_to_attempts'] = 0
        update.message.reply_text("Шаг 3/5. Введите вес посылки в кг:")
        return WEIGHT
    else:
        if attempts >= MAX_ATTEMPTS:
            update.message.reply_text("Вы ввели город неправильно 5 раз. Попробуйте оформить заявку снова.")
            return ConversationHandler.END
        else:
            update.message.reply_text("Я не знаю такого города, попробуйте ввести по-другому.")
            return CITY_TO


def weight(update, context):
    weight_str = update.message.text
    parsed_weight = parse_weight(weight_str)
    if parsed_weight is not None:
        context.user_data['weight'] = parsed_weight
        update.message.reply_text("Шаг 4/5. Введите желаемую дату отправления (дд.мм.гггг):")
        return SEND_DATE
    else:
        update.message.reply_text("Похоже, что вес введен некорректно. Пожалуйста, попробуйте еще раз.")
        return WEIGHT


def send_date(update, context):
    user_input = update.message.text
    # Заменяем некоторые разделители на стандартный
    user_input = user_input.replace(".", "-").replace("/", "-").replace(",", "-")

    try:
        parsed_date = datetime.strptime(user_input, '%d-%m-%Y').date()  # Парсим ввод пользователя
        formatted_date = parsed_date.strftime('%Y-%m-%d')  # Форматируем дату для БД

        today = date.today()  # Текущая дата
        nine_months_from_now = today + relativedelta(months=+9)  # Дата через 9 месяцев от сегодня

        if parsed_date <= today:
            update.message.reply_text("Вы ввели дату в прошлом. Пожалуйста, введите дату в будущем.")
            return SEND_DATE

        if parsed_date > nine_months_from_now:
            update.message.reply_text(
                "По вашей дате отправления совпадений не будет найдено, введите дату в пределах 9 месяцев от сегодняшнего дня.")
            return SEND_DATE

        context.user_data['send_date'] = formatted_date
        context.user_data['date_attempts'] = 0  # сбрасываем счетчик попыток
        update.message.reply_text("Шаг 5/5. Что находится внутри посылки?")
        return WHAT_IS_INSIDE
    except ValueError:
        date_attempts = context.user_data.get('date_attempts', 0) + 1  # инкрементируем счетчик попыток
        context.user_data['date_attempts'] = date_attempts

        if date_attempts >= MAX_ATTEMPTS:
            update.message.reply_text("Вы ввели дату неправильно 5 раз. Попробуйте оформить заявку снова.")
            return ConversationHandler.END
        else:
            update.message.reply_text(
                "Похоже, что формат не подходящий. Пожалуйста, введите дату в формате ДД-ММ-ГГГГ.")
            return SEND_DATE


def what_is_inside(update, context):
    context.user_data['what_is_inside'] = update.message.text
    user_data = context.user_data
    is_package = True
    username = update.message.from_user.username

    if insert_request_into_database(
            username,
            user_data.get("city_from"),
            user_data.get("city_to"),
            user_data.get("weight"),
            user_data.get("send_date"),
            user_data.get("what_is_inside"),
            is_package
    ):
        update.message.reply_text("Ваша посылка 📦 успешно сохранена.\nОна доступна в главном меню в разделе Мои заказы")
        context.user_data['conversation'] = False
    else:
        update.message.reply_text("Ошибка при сохранении вашей посылки. Попробуйте позже.")
    return ConversationHandler.END
