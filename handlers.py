import logging

from telegram.ext import CommandHandler, ConversationHandler, CallbackContext, MessageHandler, \
    Filters
from database import user_exists, insert_user_into_database
from telegram import Update

from services.delete import ASK_NUMBER, KILL_THAT_BITCH, ask_number, kill_that_bitch
from services.my_orders import my_orders
from services.show_all_orders import show_all_orders, show_city_from, show_city_to, SHOW_CITY_FROM, SHOW_CITY_TO
from services.offer_courier_service import origin_city, destination_city, comment, ORIGIN_CITY, DESTINATION_CITY, \
    COMMENT, DATE_OF_FLIGHT, \
    date_of_flight, offer_courier_service, weight2, WEIGHT2
from services.request_support import ask_for_issue, SUPPORT, forward_to_group
from services.send_package import send_package, CITY_FROM, CITY_TO, WEIGHT, SEND_DATE, \
    WHAT_IS_INSIDE, city_from, city_to, weight, send_date, what_is_inside


# Define the start command handler
def start(update, context):
    username = update.message.from_user.username  # Extract the username from the incoming message
    # Check if the user exists in the database
    if user_exists(username):
        # If user exists, send a welcome back message
        update.message.reply_text(f"Привет, {username}!")
    else:
        # If user does not exist, try to add them to the database
        if insert_user_into_database(username):
            # If insertion is successful, notify the user that account creation is successful
            update.message.reply_text("Ваш аккаунт был создан.")
        else:
            # If insertion fails, inform the user to contact support
            update.message.reply_text(
                "К сожалению, произошла ошибка при создании вашего аккаунта. Пожалуйста, напишите в поддержку.")
    # End the conversation
    return ConversationHandler.END


# Define the cancel command handler
def cancel(update: Update, context: CallbackContext):
    context.user_data.clear()  # Clear any user data that has been stored
    update.message.reply_text('Все текущие процессы отменены.')  # Inform the user that the operation has been cancelled
    return ConversationHandler.END  # End the conversation


# Define the donate command handler
def donate(update, context):
    if 'conversation' in context.user_data:
        logging.info(f"Error. User {update.message.from_user.username} tried to start new process without finishing previous.")
        update.message.reply_text(f"Вы уже находитесь в процессе создания заказа.\nЗакончите его или нажмите /cancel")
        return ConversationHandler.END
    # Send a message with the payment card information for donations
    update.message.reply_text('Карта 5312 8777 8777 8777 для Константина Маркелова.')
    return ConversationHandler.END  # End the conversation


# Define the about command handler
def about(update, context):
    if 'conversation' in context.user_data:
        logging.info(f"Error. User {update.message.from_user.username} tried to start new process without finishing previous.")
        update.message.reply_text(f"Вы уже находитесь в процессе создания заказа.\nЗакончите его или нажмите /cancel")
        return ConversationHandler.END
    # Send a message describing who created the bot and its purpose
    update.message.reply_text(
        'Константин Маркелов и Сергей Матвеев сделали для вас этот прекрасный инструмент для поиска попутчика для отправки посылки.\n\nЕсли у вас есть деньги, поделитесь с нами, пожалуйста.')
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
            SUPPORT: [MessageHandler(Filters.text & ~Filters.command, forward_to_group)]
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

    # Register each handler with the dispatcher
    dp.add_handler(support_handler)
    dp.add_handler(delete_handler)
    dp.add_handler(send_package_handler)
    dp.add_handler(all_orders_handler)
    dp.add_handler(offer_courier_service_handler)
    dp.add_handler(CommandHandler('donate', donate))
    dp.add_handler(CommandHandler('cancel', cancel))
    dp.add_handler(CommandHandler('my_orders', my_orders))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('about', about))
