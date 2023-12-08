import logging
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from constants import MAX_ATTEMPTS
from services.send_package import check_city_exists

SHOW_CITY_FROM, SHOW_CITY_TO = range(2)


def show_all_orders(update: Update, context: CallbackContext):
    logging.info(f"User {update.message.from_user.username} entered show_all_orders function.")

    if 'conversation' in context.user_data and context.user_data['conversation']:
        logging.info(f"Error. User {update.message.from_user.username} tried to start new process without finishing previous.")
        update.message.reply_text(f"Вы уже находитесь в процессе создания заказа.\nЗакончите его или нажмите /cancel")
        return ConversationHandler.END
    context.user_data['conversation'] = True

    update.message.reply_text(f"Вы находитесь в процессе поиска заказов.\n"
                              f"Закончите его или отправьте /cancel для отмены.\n\n"
                              f"Шаг 1/2. Введите город отправления:\n")
    return SHOW_CITY_FROM


def show_city_from(update: Update, context: CallbackContext):
    print_user_city = update.message.text

    if len(print_user_city) >= 50:
        update.message.reply_text("Сообщение длиннее 50 символов. Введите заново:\nДля отмены нажмите /cancel")
        return SHOW_CITY_FROM

    user_city = update.message.text.lower()
    logging.info(f"Received user city: {user_city}")

    # Инкрементируем счетчик попыток и сохраняем новое значение
    attempts = context.user_data.get('city_from_attempts', 0) + 1
    context.user_data['city_from_attempts'] = attempts

    # Проверяем существование страны
    if check_city_exists(user_city):
        context.user_data['city_from'] = user_city  # Сохраняем страну
        context.user_data['city_from_attempts'] = 0  # Сбрасываем счетчик попыток
        update.message.reply_text(f'Шаг 2/2. Теперь введите город назначения:')
        return SHOW_CITY_TO

    # Проверка количества попыток
    if attempts >= MAX_ATTEMPTS:
        update.message.reply_text("Вы ввели город неправильно 5 раз. Попробуйте оформить заявку снова.")
        return ConversationHandler.END  # Завершаем разговор
    else:
        update.message.reply_text(f"Я не знаю города {print_user_city}, попробуйте ввести по-другому.")
        return SHOW_CITY_FROM  # Продолжаем разговор


def show_city_to(update: Update, context: CallbackContext):
    print_city_to = update.message.text
    user_city_to = update.message.text.lower()
    logging.info(f"Received user city to: {user_city_to}")

    # Инкрементируем счетчик попыток и сохраняем новое значение
    attempts = context.user_data.get('city_to_attempts', 0) + 1
    context.user_data['city_to_attempts'] = attempts

    # Проверяем существование страны
    if check_city_exists(user_city_to):
        context.user_data['city_to'] = user_city_to  # Сохраняем страну
        context.user_data['city_to_attempts'] = 0  # Сбрасываем счетчик попыток

        orders = get_orders_by_countries(context.user_data['city_from'], context.user_data['city_to'])

        if not orders:
            update.message.reply_text(
                'На данный момент заказы для этих городов отсутствуют. \nВы можете поискать по ближайшим городам')
        else:
            if len(orders) > 5:
                update.message.reply_text(f'Показаны первые 5 записей из {len(orders)}.')
                orders_to_show = orders[:5]
            else:
                orders_to_show = orders

            for order in orders_to_show:
                created_at = order[7].strftime('%d.%m.%Y')
                send_date = order[5].strftime('%d.%m.%Y')

                if order[9]:
                    message_text = (f"📦 Посылка №{order[0]} от {created_at}\n"
                                    f"Кто: @{order[1]}\n"
                                    f"Откуда: {order[2].capitalize()}\n"
                                    f"Куда: {order[3].capitalize()}\n"
                                    f"Вес: {float(order[4])} кг\n"
                                    f"Желаемая дата отправки: {send_date}\n"
                                    f"Комментарий: {order[6].capitalize()}\n")
                else:
                    message_text = (f"✈️ Перевозка №{order[0]} от {created_at}\n"
                                    f"Кто: @{order[1]}\n"
                                    f"Откуда: {order[2].capitalize()}\n"
                                    f"Куда: {order[3].capitalize()}\n"
                                    f"Может взять: {float(order[4])} кг\n"
                                    f"Дата поездки: {send_date}\n"
                                    f"Комментарий: {order[6].capitalize()}\n")

                update.message.reply_text(message_text)

        context.user_data['conversation'] = False
        update.message.reply_text('Для продолжения работы перейдите в меню.')
        return ConversationHandler.END

    # Проверка количества попыток
    if attempts >= MAX_ATTEMPTS:
        update.message.reply_text("Вы ввели страну неправильно 5 раз. Попробуйте оформить заявку снова.")
        context.user_data['conversation'] = False
        return ConversationHandler.END  # Завершаем разговор
    else:
        update.message.reply_text(f"Я не знаю страны {print_city_to}, попробуйте ввести по-другому.")
        context.user_data['conversation'] = False
        return SHOW_CITY_TO  # Продолжаем разговор
