import logging
from datetime import datetime, date

from dateutil.relativedelta import relativedelta
from telegram.ext import ConversationHandler

from constants import MAX_ATTEMPTS
from database import insert_request_into_database
from services.send_package import check_city_exists, parse_weight

ORIGIN_CITY, DESTINATION_CITY, WEIGHT2, DATE_OF_FLIGHT, COMMENT = range(5)


def offer_courier_service(update, context):
    logging.info(f"User {update.message.from_user.username} entered offer_courier_service function.")

    if 'conversation' in context.user_data and context.user_data['conversation']:
        logging.info(f"Error. User {update.message.from_user.username} tried to start new process without finishing previous.")
        update.message.reply_text(f"Вы уже находитесь в процессе создания заказа.\nЗакончите его или нажмите /cancel")
        return ConversationHandler.END
    context.user_data['conversation'] = True

    update.message.reply_text(f"Вы находитесь в процессе создания нового заказа.\n"
                              f"Закончите его или отправьте /cancel для отмены.\n\n"
                              f"Шаг 1/5. Введите город отправления:\n")

    # Обнуляем счетчики попыток для всех этапов
    context.user_data['country_from_attempts'] = 0
    context.user_data['country_to_attempts'] = 0
    context.user_data['city_from_attempts'] = 0
    context.user_data['city_to_attempts'] = 0
    context.user_data['date_attempts'] = 0
    return ORIGIN_CITY


def origin_city(update, context):
    user_city = update.message.text.lower()
    attempts = context.user_data.get('city_from_attempts', 0) + 1
    context.user_data['city_from_attempts'] = attempts

    if check_city_exists(user_city):
        context.user_data['city_from'] = user_city
        context.user_data['city_from_attempts'] = 0
        update.message.reply_text("Шаг 2/5. Введите город назначения:")
        return DESTINATION_CITY
    else:
        if attempts >= MAX_ATTEMPTS:
            update.message.reply_text("Вы ввели город неправильно 5 раз. Попробуйте оформить заявку снова.")
            return ConversationHandler.END
        else:
            update.message.reply_text("Я не знаю такого города, попробуйте ввести по-другому.")
            return ORIGIN_CITY


def destination_city(update, context):
    user_city = update.message.text.lower()
    attempts = context.user_data.get('city_to_attempts', 0) + 1
    context.user_data['city_to_attempts'] = attempts

    if check_city_exists(user_city):
        context.user_data['city_to'] = user_city
        context.user_data['city_to_attempts'] = 0
        update.message.reply_text("Шаг 3/5. Сколько вы готовы примерно взять в кг:")
        return WEIGHT2
    else:
        if attempts >= MAX_ATTEMPTS:
            update.message.reply_text("Вы ввели город неправильно 5 раз. Попробуйте оформить заявку снова.")
            return ConversationHandler.END
        else:
            update.message.reply_text("Я не знаю такого города, попробуйте ввести по-другому.")
            return DESTINATION_CITY


def weight2(update, context):
    weight_str = update.message.text
    parsed_weight = parse_weight(weight_str)
    if parsed_weight is not None:
        context.user_data['weight'] = parsed_weight
        update.message.reply_text("Шаг 4/5. Введите дату полета или поездки (дд.мм.гггг):")
        return DATE_OF_FLIGHT
    else:
        update.message.reply_text("Похоже, что вес введен некорректно. Пожалуйста, попробуйте еще раз.")
        return WEIGHT2


def date_of_flight(update, context):
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
            return DATE_OF_FLIGHT

        if parsed_date > nine_months_from_now:
            update.message.reply_text(
                "По вашей дате отправления совпадений не будет найдено, введите дату в пределах 9 месяцев от сегодняшнего дня.")
            return DATE_OF_FLIGHT

        context.user_data['date_of_flight'] = formatted_date
        context.user_data['date_attempts'] = 0  # сбрасываем счетчик попыток
        update.message.reply_text("Шаг 5/5. Напишите комментарий, например, что готовы взять:")
        return COMMENT
    except ValueError:
        date_attempts = context.user_data.get('date_attempts', 0) + 1  # инкрементируем счетчик попыток
        context.user_data['date_attempts'] = date_attempts

        if date_attempts >= MAX_ATTEMPTS:
            update.message.reply_text("Вы ввели дату неправильно 5 раз. Попробуйте оформить заявку снова.")
            return ConversationHandler.END
        else:
            update.message.reply_text(
                "Похоже, что формат не подходящий. Пожалуйста, введите дату в формате ДД-ММ-ГГГГ.")
            return DATE_OF_FLIGHT


def comment(update, context):
    context.user_data["comment"] = update.message.text
    user_data = context.user_data
    username = update.message.from_user.username
    is_package = False

    if insert_request_into_database(
            username,
            user_data.get("city_from"),
            user_data.get("city_to"),
            user_data.get("weight"),
            user_data.get("date_of_flight"),
            user_data.get("comment"),
            is_package
    ):
        update.message.reply_text(
            "Ваша заявка на перевозку ✈ сохранена. \nОна доступна в главном меню в разделе Мои заказы.")
        context.user_data['conversation'] = False
    else:
        update.message.reply_text(
            "Извините, произошла ошибка. Попробуйте снова. Если ошибка повторяется, напишите в поддержку.")
    return ConversationHandler.END
