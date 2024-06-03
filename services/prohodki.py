import logging
from telegram.ext import ConversationHandler

USER_NAME_START, PLACE_START, COLLECT_USERNAME, COLLECT_DATE, LOUNGE_NAME_START = range(5)


# Utility function to check input length
def validate_input_length(update, input_text, max_length, retry_state):
    if len(input_text) >= max_length:
        update.message.reply_text(
            f"Сообщение длиннее {max_length} символов. Введите заново:\nДля отмены нажмите /cancel")
        return retry_state
    return None


def create_order(update, context):
    user = update.message.from_user.username
    logging.info(f"User {user} entered create_order function.")

    try:
        update.message.reply_text("Вы находитесь в процессе создания нового заказа.\n"
                                  "Закончите его или отправьте /cancel для отмены.\n\n"
                                  "Шаг 1/6. Введите вашу фамилию и имя на английском языке:")
        logging.info(f"Prompted user {user} to enter their name.")
        return USER_NAME_START

    except Exception as e:
        update.message.reply_text("Ошибка, напишите в поддержку")
        logging.error(f"An error occurred for user {user}: {e}")
        return ConversationHandler.END


def user_name_surname(update, context):
    user = update.message.from_user.username
    user_name = update.message.text.lower()
    logging.info(f"User {user} entered name: {user_name}")

    if validate_input_length(update, user_name, 50, USER_NAME_START):
        logging.warning(f"User {user} entered a name longer than 50 characters.")
        return USER_NAME_START

    context.user_data['user_name'] = user_name
    update.message.reply_text("Шаг 2/6. Введите город, страну и название аэропорта в котором нужна проходка")
    logging.info(f"Prompted user {user} to enter place details.")
    return PLACE_START


def place(update, context):
    user = update.message.from_user.username
    user_place = update.message.text.lower()
    logging.info(f"User {user} entered place: {user_place}")

    if validate_input_length(update, user_place, 50, PLACE_START):
        logging.warning(f"User {user} entered a place longer than 50 characters.")
        return PLACE_START

    context.user_data['user_place'] = user_place
    update.message.reply_text("Шаг 3/6. Напишите, как с вами связаться, например, юзернейм в телеграме:")
    logging.info(f"Prompted user {user} to enter contact information.")
    return COLLECT_USERNAME


def collect_username(update, context):
    user = update.message.from_user.username
    contact_info = update.message.text.lower()
    logging.info(f"User {user} entered contact info: {contact_info}")

    if validate_input_length(update, contact_info, 50, COLLECT_USERNAME):
        logging.warning(f"User {user} entered contact info longer than 50 characters.")
        return COLLECT_USERNAME

    context.user_data['contact_info'] = contact_info
    update.message.reply_text("Шаг 4/6. Введите дату когда нужна проходка:")
    logging.info(f"Prompted user {user} to enter date details.")
    return COLLECT_DATE


def collect_date(update, context):
    user = update.message.from_user.username
    user_date = update.message.text.lower()
    logging.info(f"User {user} entered date: {user_date}")

    if validate_input_length(update, user_date, 50, COLLECT_DATE):
        logging.warning(f"User {user} entered date info longer than 50 characters.")
        return COLLECT_DATE

    context.user_data['user_date'] = user_date
    update.message.reply_text("Шаг 5/6. Введите название конкретного бизнес-зала:\n"
                              "Информацию о доступных бизнес-залах обычно можно найти на сайте аэропорта или по прилету.")
    logging.info(f"Prompted user {user} to enter lounge details.")
    return LOUNGE_NAME_START


def lounge_name(update, context):
    user = update.message.from_user.username
    lounge_name = update.message.text
    logging.info(f"User {user} entered lounge name: {lounge_name}")

    if validate_input_length(update, lounge_name, 50, LOUNGE_NAME_START):
        logging.warning(f"User {user} entered a lounge name longer than 50 characters.")
        return LOUNGE_NAME_START

    context.user_data['lounge_name'] = lounge_name
    update.message.reply_text(
        "Шаг 6/6. Ваша заявка сохранена, вот детали:")
    update.message.reply_text(
                    f"Фамилия и имя: {context.user_data['user_name']}\n"
                    f"Контактные данные: {context.user_data['contact_info']}\n"
                    f"Город и страна: {context.user_data['user_place']}\n"
                    f"Дата: {context.user_data['user_date']}\n"
                    f"Бизнес-зал: {context.user_data['lounge_name']}")
    update.message.reply_text(
        "Проходка зарезервирована и ожидает оплаты в течение 30 минут.\n"
        "Переведите оплату из расчёта 999 рублей за одного человека на карту.\nНомер карты: 5280413752652326\n\n"
        "В подтверждение оплаты, пожалуйста, пришлите скриншот об оплате в данный чат боту.\n\n"
        "После оплаты в течение 15-30 минут вы получите подтверждение от оператора и QR-код. "
        "Его вместе с посадочным талоном вам нужно показать на входе в бизнес-зал. QR-код возврату и обмену не подлежит! "
        "Дети до 2-х лет проходят бесплатно. Приятного полета! :)")
    update.message.reply_text(
        "Если хотите отменить и ввести заново нажмите /cancel")
    logging.info(f"User {user} completed the order process.")
    send_data_to_group(update, context)
    return ConversationHandler.END


def send_data_to_group(update, context):
    chat_id = '-1002000757373'
    user = update.message.from_user.username
    message_text = (f"Новый заказ\n"
                    f"Фамилия и имя: {context.user_data['user_name']}\n"
                    f"Город и страна: {context.user_data['user_place']}\n"
                    f"Дата: {context.user_data['user_date']}\n"
                    f"Бизнес-зал: {context.user_data['lounge_name']}")
    context.bot.send_message(chat_id=chat_id, text=message_text)
    logging.info(f"Sent order details of user {user} to group {chat_id}.")

    message_text2 = (f"Это заказ от юзера @{user}\nКонтактные данные пользователя: {context.user_data['contact_info']}\n")
    context.bot.send_message(chat_id=chat_id, text=message_text2)
    logging.info(f"Sent user info of user {user} to group {chat_id}.")
