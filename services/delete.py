import logging

from telegram.ext import ConversationHandler

from database import mark_order_as_done

ASK_NUMBER, KILL_THAT_BITCH = range(2)


def ask_number(update, context):
    logging.info(f"User {update.message.from_user.username} entered ask_number function.")

    if 'conversation' in context.user_data and context.user_data['conversation']:
        logging.info(f"Error. User {update.message.from_user.username} tried to start new process without finishing previous.")
        update.message.reply_text(f"Вы уже находитесь в процессе создания заказа.\nЗакончите его или нажмите /cancel")
        return ConversationHandler.END
    context.user_data['conversation'] = True

    update.message.reply_text(f"Вы находитесь в процессе удаления заказа.\n"
                              f"Закончите его или отправьте /cancel для отмены.\n\n"
                              f"Шаг 1/2. Введите номер заказа:\n")
    return KILL_THAT_BITCH


def kill_that_bitch(update, context):
    order_number = update.message.text
    username = update.message.from_user.username

    for attempt in range(1, 4):  # Попытка 1-3
        if mark_order_as_done(username, order_number):
            update.message.reply_text(f"Шаг 2/2. Заказ номер {order_number} удален.")
            context.user_data['conversation'] = False
            return ConversationHandler.END
        else:
            update.message.reply_text(f"Нет заказа с номером {order_number}. Попытайтесь ввести еще раз. Попытка {attempt} из 3.")

    # На 6-й раз прерываем общение
    update.message.reply_text(f"Вы ввели 3 раза номер заказа, которого мы не можем найти. \nПроцесс удаления прерван. \nНапишите в поддержку нажав /help")
    context.user_data['conversation'] = False
    return ConversationHandler.END
