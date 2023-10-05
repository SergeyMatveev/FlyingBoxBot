from telegram.ext import CommandHandler, ConversationHandler, CallbackContext, CallbackQueryHandler, MessageHandler, \
    Filters
from database import user_exists, insert_user_into_database
from telegram import Update
from buttons import create_main_menu_buttons

# Импортировать функции и состояния из send_package.py
from services.my_orders import my_orders
from services.offer_courier_service import ORIGIN_COUNTRY, origin_country, origin_city, destination_country, \
    destination_city, comment, ORIGIN_CITY, DESTINATION_COUNTRY, DESTINATION_CITY, COMMENT, offer_courier_service
from services.request_support import ask_for_issue, SUPPORT, forward_to_group
from services.send_package import send_package, country_from, city_from, country_to, city_to, weight, COUNTRY_FROM, \
    CITY_FROM, \
    COUNTRY_TO, CITY_TO, WEIGHT, SEND_DATE, WHAT_IS_INSIDE, send_date, what_is_inside

# Импортировать функции, связанные с языком
from language import language, handle_language_choice


def display_menu(update: Update, context: CallbackContext):
    buttons_markup = create_main_menu_buttons()  # Create the inline keyboard buttons
    update.message.reply_text("Выберите действие:", reply_markup=buttons_markup)


def start(update, context):
    username = update.message.from_user.username
    # Check if the user exists in the database
    if user_exists(username):
        update.message.reply_text(f"Привет, {username}!")
    else:
        # User doesn't exist, insert into the database and ask about language
        if insert_user_into_database(username):
            update.message.reply_text("Ваш аккаунт был создан.")
        else:
            update.message.reply_text("К сожалению, произошла ошибка при создании вашего аккаунта. Пожалуйста, напишите в поддержку.")
    display_menu(update, context)
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    context.user_data.clear()  # очищаем пользовательские данные
    if update.message:
        update.message.reply_text('Операция отменена.')
    elif update.callback_query:
        update.callback_query.answer()
        update.callback_query.edit_message_text('Операция отменена.')
    return ConversationHandler.END


def setup_handlers(updater):
    dp = updater.dispatcher

    send_package_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(send_package, pattern='^send_package$')],
        states={
            COUNTRY_FROM: [MessageHandler(Filters.text & ~Filters.command, country_from)],
            CITY_FROM: [MessageHandler(Filters.text & ~Filters.command, city_from)],
            COUNTRY_TO: [MessageHandler(Filters.text & ~Filters.command, country_to)],
            CITY_TO: [MessageHandler(Filters.text & ~Filters.command, city_to)],
            WEIGHT: [MessageHandler(Filters.text & ~Filters.command, weight)],
            SEND_DATE: [MessageHandler(Filters.text & ~Filters.command, send_date)],
            WHAT_IS_INSIDE: [MessageHandler(Filters.text & ~Filters.command, what_is_inside)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    offer_courier_service_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(offer_courier_service, pattern='^offer_courier_service$')],
        states={
            ORIGIN_COUNTRY: [MessageHandler(Filters.text & ~Filters.command, origin_country)],
            ORIGIN_CITY: [MessageHandler(Filters.text & ~Filters.command, origin_city)],
            DESTINATION_COUNTRY: [MessageHandler(Filters.text & ~Filters.command, destination_country)],
            DESTINATION_CITY: [MessageHandler(Filters.text & ~Filters.command, destination_city)],
            COMMENT: [MessageHandler(Filters.text & ~Filters.command, comment)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    support_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(ask_for_issue, pattern='^request_support$')],
        states={
            SUPPORT: [MessageHandler(Filters.text & ~Filters.command, forward_to_group)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(support_handler)
    dp.add_handler(CommandHandler('start', display_menu))
    dp.add_handler(CommandHandler('language', language))
    dp.add_handler(CommandHandler('cancel', cancel))
    dp.add_handler(send_package_handler)
    dp.add_handler(offer_courier_service_handler)
    dp.add_handler(CallbackQueryHandler(handle_language_choice, pattern='^lang_'))
    dp.add_handler(CallbackQueryHandler(my_orders, pattern='^my_orders$'))
