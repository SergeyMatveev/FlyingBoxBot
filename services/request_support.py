import logging

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

FORWARD_TO_GROUP = range(1)

GROUP_CHAT_ID = '-1001837659021'


def ask_for_issue(update: Update, context: CallbackContext):
    logging.info(f"User {update.message.from_user.username} entered ask_for_issue function.")
    if 'conversation' in context.user_data and context.user_data['conversation']:
        logging.info(f"Error. User {update.message.from_user.username} tried to start new process without finishing previous.")
        update.message.reply_text(f"Вы уже находитесь в процессе создания заказа.\nЗакончите его или нажмите /cancel")
        return ConversationHandler.END
    context.user_data['conversation'] = True
    """Обработчик кнопки помощь."""
    update.message.reply_text("Напишите, что пошло не так:")
    return FORWARD_TO_GROUP


def forward_to_group(update: Update, context: CallbackContext):
    context.user_data['support'] = update.message.text

    if len(context.user_data['support']) >= 50:
        update.message.reply_text("Сообщение длиннее 50 символов. Введите заново:\nДля отмены нажмите /cancel")
        return FORWARD_TO_GROUP

    user_message = update.message.text
    user_username = update.message.from_user.username
    context.bot.send_message(GROUP_CHAT_ID, f"Сообщение от пользователя @{user_username}: {user_message}")
    update.message.reply_text("Спасибо за обращение! Мы рассмотрим вашу проблему как можно скорее, и вернемся к вам с ответом.")
    context.user_data['conversation'] = False
    return ConversationHandler.END
