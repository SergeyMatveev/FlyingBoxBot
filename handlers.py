import logging

from telegram.ext import CommandHandler, ConversationHandler, CallbackContext, MessageHandler, \
    Filters
from database import get_unique_usernames, export_requests_to_csv_and_upload, \
    save_order_in_database
from telegram import Update

from services.delete import ASK_NUMBER, KILL_THAT_BITCH, ask_number, kill_that_bitch
from services.matching import matching, MATCHING, prepare_matching, PREPARE_MATCHING
from services.my_orders import my_orders
from services.show_all_orders import show_all_orders, show_city_from, show_city_to, SHOW_CITY_FROM, SHOW_CITY_TO
from services.offer_courier_service import origin_city, destination_city, comment, ORIGIN_CITY, DESTINATION_CITY, \
    COMMENT, DATE_OF_FLIGHT, \
    date_of_flight, offer_courier_service, weight2, WEIGHT2
from services.request_support import ask_for_issue, FORWARD_TO_GROUP, forward_to_group
from services.send_package import send_package, CITY_FROM, CITY_TO, WEIGHT, SEND_DATE, \
    WHAT_IS_INSIDE, city_from, city_to, weight, send_date, what_is_inside


# Define the start command handler
def start(update, context):
    logging.info(f"User {update.message.from_user.username} entered start function.")
    username = update.message.from_user.username  # Extract the username from the incoming message
    update.message.reply_text(f"Здравствуйте! Вы успешно зарегистрировались во Flyingbox боте. Мы надеемся, что наш бот будет полезен, а отправка мелких грузов станет проще. "
                              f"\n\nПодписывайтесь на наш канал @flyingbox! Там вы сможете прочитать и найти:"
                              f"\n- подробную инструкцию по использованию бота,"
                              f"\n- полезную информацию о перевозках,"
                              f"\n- сможете задать вопрос о работе бота."
                              f"\n@flyingbox")
    return ConversationHandler.END


# Define the cancel command handler
def cancel(update: Update, context: CallbackContext):
    logging.info(f"User {update.message.from_user.username} entered cancel function.")
    context.user_data.clear()  # Clear any user data that has been stored
    update.message.reply_text('Действие отменено.\nВ меню вы найдете список доступных действий.')  # Inform the user that the operation has been cancelled
    return ConversationHandler.END  # End the conversation


# CD = create default order
def cd(update: Update, context: CallbackContext):
    logging.info(f"User {update.message.from_user.username} entered create default order function.")
    user_data = context.user_data
    is_package = True
    username = update.message.from_user.username
    chat_id = update.message.chat_id

    # insert_request_into_database now returns the order ID instead of True/False
    order_id = save_order_in_database(
        username,
        'осло',
        'осло',
        11,
        '2023-12-11',
        'тест',
        is_package,
        chat_id
    )
    if order_id is not None:
        # Include the order ID in the success message
        update.message.reply_text(
            f"Посылка 📦 №{order_id} успешно сохранена.")
        update.message.reply_text("Сейчас будет показаны подходящие заказы.")
        context.user_data['request_id'] = order_id
        context.user_data['cascade'] = True
        prepare_matching(update, context)
    else:
        update.message.reply_text("Ошибка при сохранении посылки.")
    return ConversationHandler.END


# Define the donate command handler
def donate(update, context):
    logging.info(f"User {update.message.from_user.username} entered donate function.")
    if 'conversation' in context.user_data and context.user_data['conversation']:
        logging.info(f"Error. User {update.message.from_user.username} tried to start new process without finishing previous.")
        update.message.reply_text(f"Вы уже находитесь в процессе создания заказа.\nЗакончите его или нажмите /cancel")
        return ConversationHandler.END
    # Send a message with the payment card information for donations
    update.message.reply_text(f'Если вам понравился бот, вы можете помочь развивать его сделав перевод по номеру карты Тинькофф 5280 4137 5265 2326 \n\nЗаранее спасибо :)')
    return ConversationHandler.END  # End the conversation


def users_count(update, context):
    logging.info(f"User {update.message.from_user.username} entered users_count function.")
    if 'conversation' in context.user_data and context.user_data['conversation']:
        logging.info(f"Error. User {update.message.from_user.username} tried to start new process without finishing previous.")
        update.message.reply_text(f"Вы уже находитесь в процессе создания заказа.\nЗакончите его или нажмите /cancel")
        return ConversationHandler.END
    # Send a message with the payment card information for donations
    users = get_unique_usernames()
    update.message.reply_text(f'У нас в базе {len(users)} юзеров.')
    return ConversationHandler.END  # End the conversation


def refresh_db_backup(update, context):
    logging.info(f"User {update.message.from_user.username} entered refresh_db_backup function.")
    if 'conversation' in context.user_data and context.user_data['conversation']:
        logging.info(f"Error. User {update.message.from_user.username} tried to start new process without finishing previous.")
        update.message.reply_text(f"Вы уже находитесь в процессе создания заказа.\nЗакончите его или нажмите /cancel")
        return ConversationHandler.END
    # Send a message with the payment card information for donations
    if export_requests_to_csv_and_upload():
        update.message.reply_text(f"Обновились данные. Проверьте гугл драйв.")
        return ConversationHandler.END  # End the conversation
    else:
        update.message.reply_text(f"Что-то на*бнулось.")
        return ConversationHandler.END  # End the conversation


# Define the about command handler
def about(update, context):
    logging.info(f"User {update.message.from_user.username} entered about function.")
    if 'conversation' in context.user_data and context.user_data['conversation']:
        logging.info(f"Error. User {update.message.from_user.username} tried to start new process without finishing previous.")
        update.message.reply_text(f"Вы уже находитесь в процессе создания заказа.\nЗакончите его или нажмите /cancel")
        return ConversationHandler.END
    # Send a message describing who created the bot and its purpose
    update.message.reply_text(
        'Мы - команда молодого чат-бота @flying_box_bot \nРешили сделать этот мир чуточку лучше. Мы лично столкнулись с задачей передачи мелких пакетов и грузов из/в РФ и придумали вот такого бота в помощь всем. \nБот полностью бесплатный, но если он принес вам пользу и понравился - будем рады вашим донатам. \n\nСпасибо :)')
    return ConversationHandler.END  # End the conversation


# Setup the command handlers for the telegram bot
def setup_handlers(updater):
    dp = updater.dispatcher  # Get the dispatcher from the updater

    # Create and add a conversation handler for the 'send package' workflow
    send_package_handler = ConversationHandler(
        entry_points=[CommandHandler('send', send_package)],
        states={
            CITY_FROM: [MessageHandler(Filters.text & ~Filters.command, city_from)],
            CITY_TO: [MessageHandler(Filters.text & ~Filters.command, city_to)],
            WEIGHT: [MessageHandler(Filters.text & ~Filters.command, weight)],
            SEND_DATE: [MessageHandler(Filters.text & ~Filters.command, send_date)],
            WHAT_IS_INSIDE: [MessageHandler(Filters.text & ~Filters.command, what_is_inside)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Create and add a conversation handler for the 'offer courier service' workflow
    offer_courier_service_handler = ConversationHandler(
        entry_points=[CommandHandler('courier', offer_courier_service)],
        states={
            ORIGIN_CITY: [MessageHandler(Filters.text & ~Filters.command, origin_city)],
            DESTINATION_CITY: [MessageHandler(Filters.text & ~Filters.command, destination_city)],
            WEIGHT2: [MessageHandler(Filters.text & ~Filters.command, weight2)],
            DATE_OF_FLIGHT: [MessageHandler(Filters.text & ~Filters.command, date_of_flight)],
            COMMENT: [MessageHandler(Filters.text & ~Filters.command, comment)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Create and add a conversation handler for the support workflow
    support_handler = ConversationHandler(
        entry_points=[CommandHandler('help', ask_for_issue)],
        states={
            FORWARD_TO_GROUP: [MessageHandler(Filters.text & ~Filters.command, forward_to_group)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Create and add a conversation handler for showing all orders
    all_orders_handler = ConversationHandler(
        entry_points=[CommandHandler('all_orders', show_all_orders)],
        states={
            SHOW_CITY_FROM: [MessageHandler(Filters.text & ~Filters.command, show_city_from)],
            SHOW_CITY_TO: [MessageHandler(Filters.text & ~Filters.command, show_city_to)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Create and add a conversation handler for deleting orders
    delete_handler = ConversationHandler(
        entry_points=[CommandHandler('delete', ask_number)],
        states={
            ASK_NUMBER: [MessageHandler(Filters.text & ~Filters.command, ask_number)],
            KILL_THAT_BITCH: [MessageHandler(Filters.text & ~Filters.command, kill_that_bitch)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # метчинг
    matching_handler = ConversationHandler(
        entry_points=[CommandHandler('matching', prepare_matching)],
        states={
            PREPARE_MATCHING: [MessageHandler(Filters.text & ~Filters.command, prepare_matching)],
            MATCHING: [MessageHandler(Filters.text & ~Filters.command, matching)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Register each handler with the dispatcher
    dp.add_handler(support_handler)
    dp.add_handler(delete_handler)
    dp.add_handler(send_package_handler)
    dp.add_handler(all_orders_handler)
    dp.add_handler(offer_courier_service_handler)
    dp.add_handler(matching_handler)

    dp.add_handler(CommandHandler('donate', donate))
    dp.add_handler(CommandHandler('cancel', cancel))
    dp.add_handler(CommandHandler('my_orders', my_orders))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('about', about))
    dp.add_handler(CommandHandler('users_count', users_count))
    dp.add_handler(CommandHandler('refresh_db_backup', refresh_db_backup))
    dp.add_handler(CommandHandler('cd', cd))
