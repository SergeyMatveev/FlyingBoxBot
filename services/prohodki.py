import logging

from telegram.ext import ConversationHandler

USER_NAME_START, PLACE_START, LOUNGE_NAME_START = range(3)


def create_order(update, context):
    logging.info(f"User {update.message.from_user.username} entered create_order function.")

    try:
        update.message.reply_text(f"Вы находитесь в процессе создания нового заказа.\n"
                                  f"Закончите его или отправьте /cancel для отмены.\n\n"
                                  f"Шаг 1/4. Введите вашу фамилию и имя:\n")

        return USER_NAME_START

    except Exception as e:
        update.message.reply_text(f"Ошибка, напишите в поддержку")
        logging.error(f"An error occurred: {e}")
        return ConversationHandler.END


def user_name(update, context):
    user_name = update.message.text.lower()

    if len(user_name) >= 50:
        update.message.reply_text("Сообщение длиннее 50 символов. Введите заново:\nДля отмены нажмите /cancel")
        return USER_NAME_START

    context.user_data['user_name'] = user_name

    update.message.reply_text(f"Шаг 2/4. Введите город, страну и название аэропорта в котором нужна проходка")

    return PLACE_START


def place(update, context):
    user_place = update.message.text.lower()
    attempts = context.user_data.get('city_to_attempts', 0) + 1
    context.user_data['city_to_attempts'] = attempts

    if len(user_place) >= 50:
        update.message.reply_text("Сообщение длиннее 50 символов. Введите заново:\nДля отмены нажмите /cancel")
        return PLACE_START

    context.user_data['user_place'] = user_place

    update.message.reply_text(
        f"Шаг 3/4. Введите название конкретного бизнес-зала и дату когда вам нужен проход:\nИнформацию обычно можно найти на сайте или по прилету в аэропорту.")

    return LOUNGE_NAME_START


def lounge_name(update, context):
    lounge_name = update.message.text

    if len(lounge_name) >= 50:
        update.message.reply_text("Сообщение длиннее 50 символов. Введите заново:\nДля отмены нажмите /cancel")
        return LOUNGE_NAME_START

    context.user_data['lounge_name'] = lounge_name

    send_data_to_group(update, context)

    update.message.reply_text(
        "Шаг 4/4. Ваша заявка сохранена и ожидает оплаты.\nПереведите оплату из расчёта 900 рублей за одного "
        "человека\nНомер карты 5280413752652326\n\nВ подтверждении оплаты, пожалуйста, пришлите скрин об оплате в данный чат.\n\n"
        "После оплаты в течение 15-30 минут вы получите подтверждение от оператора и QR-код от бота. QR-код вместе с "
        "посадочным талоном вам нужно показать на входе в бизнес зал.")

    return ConversationHandler.END


def send_data_to_group(update, context):
    chat_id = '-1002000757373'
    message_text = (f"Новый заказ\n"
                    f"Фамилия и имя: {context.user_data['user_name']}\n"
                    f"Город и страна: {context.user_data['user_place']}\n"
                    f"Бизнес-зал: {context.user_data['lounge_name']}")
    message_text = (f"Это заказ от юзера @{update.message.from_user.username}")
    context.bot.send_message(chat_id=chat_id, text=message_text)
