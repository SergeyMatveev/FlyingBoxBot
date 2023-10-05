from telegram.ext import MessageHandler, Filters, ConversationHandler
from database import insert_route_into_database

ORIGIN_COUNTRY, ORIGIN_CITY, DESTINATION_COUNTRY, DESTINATION_CITY, COMMENT = range(5)


def offer_courier_service(update, context):
    update.callback_query.message.reply_text("From which country are you offering the courier service?")
    return ORIGIN_COUNTRY


def origin_country(update, context):
    context.user_data['origin_country'] = update.message.text
    update.message.reply_text("From which city?")
    return ORIGIN_CITY


def origin_city(update, context):
    context.user_data['origin_city'] = update.message.text
    update.message.reply_text("To which destination country are you offering the courier service?")
    return DESTINATION_COUNTRY


def destination_country(update, context):
    context.user_data['destination_country'] = update.message.text
    update.message.reply_text("To which destination city?")
    return DESTINATION_CITY


def destination_city(update, context):
    context.user_data['destination_city'] = update.message.text
    update.message.reply_text("Any additional comments about your service?")
    return COMMENT


def comment(update, context):
    context.user_data["comment"] = update.message.text

    user_data = context.user_data
    username = update.message.from_user.username

    if insert_route_into_database(
            username,
            user_data.get("origin_country"),
            user_data.get("origin_city"),
            user_data.get("destination_country"),
            user_data.get("destination_city"),
            user_data.get("comment")
    ):
        update.message.reply_text("Your courier service offer has been saved.")
    else:
        update.message.reply_text("Sorry, there was an error saving your offer. Please try again later.")
    return ConversationHandler.END
