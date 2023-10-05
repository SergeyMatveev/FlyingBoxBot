from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters, ConversationHandler

SUPPORT = range(1)

GROUP_CHAT_ID = '-4091157408'


def ask_for_issue(update: Update, context: CallbackContext) -> None:
    """Обработчик кнопки помощь."""
    update.callback_query.message.reply_text("Напишите, что пошло не так:")
    return SUPPORT


def forward_to_group(update: Update, context: CallbackContext) -> None:
    context.user_data['support'] = update.message.text
    user_message = update.message.text
    user_username = update.message.from_user.username
    context.bot.send_message(GROUP_CHAT_ID, f"Сообщение от пользователя {user_username}: {user_message}")
    update.message.reply_text("Спасибо за ваше обращение! Мы рассмотрим вашу проблему как можно скорее.")
    return ConversationHandler.END
