import logging

from telegram.ext import CommandHandler, ConversationHandler, CallbackContext, MessageHandler, \
    Filters
from telegram import Update

from services.delete import ASK_NUMBER, KILL_THAT_BITCH, ask_number, kill_that_bitch
from services.matching import matching, MATCHING, prepare_matching, PREPARE_MATCHING
from services.my_orders import my_orders
from services.offer_courier_service import origin_city, destination_city, comment, ORIGIN_CITY, DESTINATION_CITY, \
    COMMENT, DATE_OF_FLIGHT, \
    date_of_flight, offer_courier_service, weight2, WEIGHT2
from services.prohodki import create_order, user_name, USER_NAME_START, PLACE_START, LOUNGE_NAME_START, place, \
    lounge_name
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
    update.message.reply_text(
        f'После запуска бота вам будут доступны следующие пункты меню:\n'
        f'- /send - опубликовать посылку к отправке\n'
        f'- /courier - опубликовать перевозку - если вы летите и готовы перевезти что-то попутно\n'
        f'- /my-orders - просмотреть созданные вами заказы и удалить, если нужно\n'
        f'- /cancel - отменяет последнее действие/операцию\n'
        f'- /help - тут можно описать проблему и мы поможем ее решить\n'
        f'- /donate - помочь нам и поддержать проект\n'
        f'- /about - информация о нас и краткая справка')

    chat_id = update.message.chat_id
    update.message.reply_text(f'ID этого чата: {chat_id}')

    return ConversationHandler.END


# Define the cancel command handler
def cancel(update: Update, context: CallbackContext):
    logging.info(f"User {update.message.from_user.username} entered cancel function.")
    context.user_data.clear()  # Clear any user data that has been stored
    update.message.reply_text('Действие отменено.\nВ меню вы найдете список доступных действий.')  # Inform the user that the operation has been cancelled
    return ConversationHandler.END  # End the conversation


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
    update.message.reply_text(
        f'После запуска бота вам будут доступны следующие пункты меню:\n'
        f'- /send - опубликовать посылку к отправке\n'
        f'- /courier - опубликовать перевозку - если вы летите и готовы перевезти что-то попутно\n'
        f'- /my-orders - просмотреть созданные вами заказы и удалить, если нужно\n'
        f'- /cancel - отменяет последнее действие/операцию\n'
        f'- /help - тут можно описать проблему и мы поможем ее решить\n'
        f'- /donate - помочь нам и поддержать проект\n'
        f'- /about - информация о нас и краткая справка')

    return ConversationHandler.END  # End the conversation


def forward_photo(update: Update, context: CallbackContext) -> None:
    chat_id = '-1002000757373'  # ID группы, куда нужно переслать фото
    # Извлекаем имя и фамилию пользователя из сохраненных данных
    user_name = context.user_data.get('user_name', 'Неизвестный пользователь')
    username = update.message.from_user.username

    # Получаем объект фотографии с наивысшим разрешением
    photo_file = update.message.photo[-1].get_file()
    # Скачиваем фото
    photo_file.download('photo.jpg')

    # Отправляем фото в группу с подписью, содержащей имя и фамилию
    caption = f"Фото от {user_name}, @{username}"
    context.bot.send_photo(chat_id=chat_id, photo=open('photo.jpg', 'rb'), caption=caption)
    update.message.reply_text(f"Спасибо! Ожидайте QR-код. Среднее время ожидания 15 минут.\nЕсли у вас возникнут вопросы, свяжитесь с нами /help")


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

    # Create and add a conversation handler for the 'send package' workflow
    create_order_handler = ConversationHandler(
        entry_points=[CommandHandler('lounge', create_order)],
        states={
            USER_NAME_START: [MessageHandler(Filters.text & ~Filters.command, user_name)],
            PLACE_START: [MessageHandler(Filters.text & ~Filters.command, place)],
            LOUNGE_NAME_START: [MessageHandler(Filters.text & ~Filters.command, lounge_name)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Register each handler with the dispatcher
    dp.add_handler(support_handler)
    dp.add_handler(delete_handler)
    dp.add_handler(send_package_handler)
    dp.add_handler(offer_courier_service_handler)
    dp.add_handler(matching_handler)
    dp.add_handler(create_order_handler)

    dp.add_handler(CommandHandler('donate', donate))
    dp.add_handler(CommandHandler('cancel', cancel))
    dp.add_handler(CommandHandler('my_orders', my_orders))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('about', about))
    photo_handler = MessageHandler(Filters.photo, forward_photo)
    dp.add_handler(photo_handler)

