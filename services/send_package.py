from telegram.ext import CallbackQueryHandler, MessageHandler, Filters, ConversationHandler

from constants import KNOWN_COUNTRIES, KNOWN_CITIES
from database import insert_request_into_database
from datetime import datetime, date
import re
from dateutil.relativedelta import relativedelta

COUNTRY_FROM, CITY_FROM, COUNTRY_TO, CITY_TO, WEIGHT, SEND_DATE, WHAT_IS_INSIDE = range(7)
MAX_ATTEMPTS = 5  # максимальное количество попыток ввода


def parse_weight(weight_str):
    weight_str = weight_str.replace(',', '.')
    match = re.search(r'(\d+(\.\d+)?)', weight_str)
    if match:
        return float(match.group(1))
    else:
        return None


def check_country_exists(country):
    return country.lower() in KNOWN_COUNTRIES


def check_city_exists(city):
    return city.lower() in KNOWN_CITIES


def send_package(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Введите страну отправления:")

    # Обнуляем счетчики попыток для всех этапов
    context.user_data['country_from_attempts'] = 0
    context.user_data['country_to_attempts'] = 0
    context.user_data['city_from_attempts'] = 0
    context.user_data['city_to_attempts'] = 0
    context.user_data['date_attempts'] = 0

    return COUNTRY_FROM


def country_from(update, context):
    user_country = update.message.text.lower()
    attempts = context.user_data.get('country_from_attempts', 0) + 1  # инкрементируем счетчик попыток
    context.user_data['country_from_attempts'] = attempts  # сохраняем новое значение

    if check_country_exists(user_country):
        context.user_data['country_from'] = user_country  # сохраняем страну
        context.user_data['country_from_attempts'] = 0  # сбрасываем счетчик попыток
        update.message.reply_text("Введите город отправления:")
        return CITY_FROM
    else:
        if attempts >= MAX_ATTEMPTS:  # если количество попыток достигло максимума
            update.message.reply_text("Вы ввели страну неправильно 5 раз. Попробуйте оформить заявку снова.")
            return ConversationHandler.END  # завершаем разговор
        else:
            update.message.reply_text("Я не знаю такой страны, попробуйте ввести по-другому.")
            return COUNTRY_FROM  # продолжаем разговор


def city_from(update, context):
    user_city = update.message.text.lower()
    attempts = context.user_data.get('city_from_attempts', 0) + 1
    context.user_data['city_from_attempts'] = attempts

    if check_city_exists(user_city):
        context.user_data['city_from'] = user_city
        context.user_data['city_from_attempts'] = 0
        update.message.reply_text("Введите страну назначения:")
        return COUNTRY_TO
    else:
        if attempts >= MAX_ATTEMPTS:
            update.message.reply_text("Вы ввели город неправильно 5 раз. Попробуйте оформить заявку снова.")
            return ConversationHandler.END
        else:
            update.message.reply_text("Я не знаю такого города, попробуйте ввести по-другому.")
            return CITY_FROM


def country_to(update, context):
    user_country = update.message.text.lower()
    attempts = context.user_data.get('country_to_attempts', 0) + 1  # инкрементируем счетчик попыток
    context.user_data['country_to_attempts'] = attempts  # сохраняем новое значение

    if check_country_exists(user_country):
        context.user_data['country_to'] = user_country  # сохраняем страну
        context.user_data['country_to_attempts'] = 0  # сбрасываем счетчик попыток
        update.message.reply_text("Введите город назначения:")
        return CITY_TO
    else:
        if attempts >= MAX_ATTEMPTS:  # если количество попыток достигло максимума
            update.message.reply_text("Вы ввели страну неправильно 5 раз. Попробуйте оформить заявку снова.")
            return ConversationHandler.END  # завершаем разговор
        else:
            update.message.reply_text("Я не знаю такой страны, попробуйте ввести по-другому.")
            return COUNTRY_TO  # продолжаем разговор


def city_to(update, context):
    user_city = update.message.text.lower()
    attempts = context.user_data.get('city_to_attempts', 0) + 1
    context.user_data['city_to_attempts'] = attempts

    if check_city_exists(user_city):
        context.user_data['city_to'] = user_city
        context.user_data['city_to_attempts'] = 0
        update.message.reply_text("Введите вес посылки в кг:")
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
        update.message.reply_text("Введите желаемую дату отправления (дд-мм-гггг):")
        return SEND_DATE
    else:
        update.message.reply_text("Похоже, что вес введен некорректно. Пожалуйста, попробуйте еще раз.")
        return WEIGHT


def send_date(update, context):
    user_input = update.message.text
    try:
        parsed_date = datetime.strptime(user_input, '%d-%m-%Y').date()  # Парсим ввод пользователя
        formatted_date = parsed_date.strftime('%Y-%m-%d')  # Форматируем дату для БД

        today = date.today()  # Текущая дата
        nine_months_from_now = today + relativedelta(months=+9)  # Дата через 9 месяцев от сегодня

        if parsed_date <= today:
            update.message.reply_text("Вы ввели дату в прошлом. Пожалуйста, введите дату в будущем.")
            return SEND_DATE

        if parsed_date > nine_months_from_now:
            update.message.reply_text("По вашей дате отправления совпадений не будет найдено, введите дату в пределах 9 месяцев от сегодняшнего дня.")
            return SEND_DATE

        context.user_data['send_date'] = formatted_date
        context.user_data['date_attempts'] = 0  # сбрасываем счетчик попыток
        update.message.reply_text("Что находится внутри посылки?")
        return WHAT_IS_INSIDE
    except ValueError:
        date_attempts = context.user_data.get('date_attempts', 0) + 1  # инкрементируем счетчик попыток
        context.user_data['date_attempts'] = date_attempts

        if date_attempts >= MAX_ATTEMPTS:
            update.message.reply_text("Вы ввели дату неправильно 5 раз. Попробуйте оформить заявку снова.")
            return ConversationHandler.END
        else:
            update.message.reply_text("Похоже, что формат не подходящий. Пожалуйста, введите дату в формате ДД-ММ-ГГГГ.")
            return SEND_DATE


def what_is_inside(update, context):
    context.user_data['what_is_inside'] = update.message.text
    user_data = context.user_data
    username = update.message.from_user.username
    if insert_request_into_database(
            username,
            user_data.get("country_from"),
            user_data.get("city_from"),
            user_data.get("country_to"),
            user_data.get("city_to"),
            user_data.get("weight"),
            user_data.get("send_date"),
            user_data.get("what_is_inside")
    ):
        update.message.reply_text("Ваша заявка сохранена.")
    else:
        update.message.reply_text("Ошибка при сохранении вашей заявки. Попробуйте позже.")
    return ConversationHandler.END
