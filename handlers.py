from telegram.ext import CommandHandler, ConversationHandler, CallbackContext, CallbackQueryHandler, MessageHandler, \
    Filters
from database import user_exists, insert_user_into_database, update_user_language
from telegram import Update
from buttons import create_inline_buttons, create_language_buttons

# Импортировать функции и состояния из send_package.py
from send_package import send_package, country_from, city_from, country_to, city_to, weight, COUNTRY_FROM, CITY_FROM, \
    COUNTRY_TO, CITY_TO, WEIGHT

# Импортировать функции, связанные с языком
from language import language, handle_language_choice


def display_menu(update: Update, context: CallbackContext):
    buttons_markup = create_inline_buttons()  # Create the inline keyboard buttons
    update.message.reply_text("Choose an option:", reply_markup=buttons_markup)


def start(update, context):
    username = update.message.from_user.username
    # Check if the user exists in the database
    if user_exists(username):
        update.message.reply_text(f"Hello, {username}!")
    else:
        # User doesn't exist, insert into the database and ask about language
        if insert_user_into_database(username):
            update.message.reply_text("Your account has been created.")
        else:
            update.message.reply_text("Sorry, there was an error creating your account. Please try again later.")
    display_menu(update, context)
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END


def setup_handlers(updater):
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CallbackQueryHandler(send_package, pattern='^send_package$')],
        states={
            COUNTRY_FROM: [MessageHandler(Filters.text & ~Filters.command, country_from)],
            CITY_FROM: [MessageHandler(Filters.text & ~Filters.command, city_from)],
            COUNTRY_TO: [MessageHandler(Filters.text & ~Filters.command, country_to)],
            CITY_TO: [MessageHandler(Filters.text & ~Filters.command, city_to)],
            WEIGHT: [MessageHandler(Filters.text & ~Filters.command, weight)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('language', language))
    dp.add_handler(CallbackQueryHandler(handle_language_choice, pattern='^lang_'))
