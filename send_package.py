from telegram.ext import CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
from database import insert_request_into_database

COUNTRY_FROM, CITY_FROM, COUNTRY_TO, CITY_TO, WEIGHT = range(5)


def send_package(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="From which country would you like to send the package?")
    return COUNTRY_FROM


def country_from(update, context):
    context.user_data['country_from'] = update.message.text
    update.message.reply_text("From which city?")
    return CITY_FROM


def city_from(update, context):
    context.user_data['city_from'] = update.message.text
    update.message.reply_text("What is the country of destination?")
    return COUNTRY_TO


def country_to(update, context):
    context.user_data['country_to'] = update.message.text
    update.message.reply_text("What is the city of destination?")
    return CITY_TO


def city_to(update, context):
    context.user_data['city_to'] = update.message.text
    update.message.reply_text("Please describe the package (what it is, weight, volume...)")
    return WEIGHT


def weight(update, context):
    context.user_data["weight"] = update.message.text
    user_data = context.user_data
    username = update.message.from_user.username
    if insert_request_into_database(
            username,
            user_data.get("country_from"),
            user_data.get("city_from"),
            user_data.get("country_to"),
            user_data.get("city_to"),
            user_data.get("weight")
    ):
        update.message.reply_text("Your request has been saved.")
    else:
        update.message.reply_text("Sorry, there was an error saving your request. Please try again later.")
    return ConversationHandler.END
