from telegram.ext import CommandHandler, ConversationHandler, CallbackContext
from database import user_exists, insert_user_into_database
from telegram import Update
from buttons import create_inline_buttons


def display_menu(update: Update, context: CallbackContext):
    buttons_markup = create_inline_buttons()  # Create the inline keyboard buttons
    update.message.reply_text("Choose an option:", reply_markup=buttons_markup)


def start(update, context):
    username = update.message.from_user.username

    # Check if the user exists in the database
    if user_exists(username):
        update.message.reply_text(f"Hello, {username}!")
    else:
        # User doesn't exist, insert into the database
        if insert_user_into_database(username):
            update.message.reply_text("Your account has been created.")
        else:
            update.message.reply_text("Sorry, there was an error creating your account. Please try again later.")

    display_menu(update, context)

    return ConversationHandler.END


def setup_handlers(updater):
    dp = updater.dispatcher

    # Add a command handler for the /start command
    dp.add_handler(CommandHandler("start", start))

    return dp
