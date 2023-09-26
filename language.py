from database import update_user_language
from telegram import Update
from buttons import create_language_buttons
from telegram.ext import ConversationHandler, CallbackContext


def language(update: Update, context: CallbackContext):
    keyboard = create_language_buttons()
    update.message.reply_text('Please choose your language:', reply_markup=keyboard)
    return


def handle_language_choice(update: Update, context: CallbackContext):
    query = update.callback_query
    lang_data = query.data
    username = update.callback_query.from_user.username

    if lang_data == 'lang_en':
        # Запись 1 в базу данных
        if update_user_language(username, 1):
            query.edit_message_text("Language set to English.")
        else:
            query.edit_message_text("Can not update the language. Please request a support.")
    elif lang_data == 'lang_ru':
        # Запись 2 в базу данных
        if update_user_language(username, 2):
            query.edit_message_text("Язык установлен на русский.")
        else:
            query.edit_message_text("Ошибка установки языка, обратитесь в поддержку.")

    return ConversationHandler.END
