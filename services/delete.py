import logging

from telegram.ext import ConversationHandler

from database import mark_order_as_completed

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
    username = update.message.from_user.username

    # Получаем номер заказа, введенный пользователем
    order_number = update.message.text.strip()

    if len(order_number) >= 50:
        update.message.reply_text("Сообщение длиннее 50 символов. Введите заново:\nДля отмены нажмите /cancel")
        return KILL_THAT_BITCH

    # Проверяем, является ли order_number целым числом
    if order_number.isdigit():
        order_number = int(order_number)  # Преобразуем строку в int

        # Пытаемся пометить заказ как выполненный, если он существует
        if mark_order_as_completed(username, order_number):
            update.message.reply_text(f"Шаг 2/2. Заказ номер {order_number} удален.")
            context.user_data['conversation'] = False
            return ConversationHandler.END
        else:
            update.message.reply_text("Шаг 2/2. Заказ с таким номером не найден. \nНачните процесс заново нажав /delete")
            context.user_data['conversation'] = False
            return ConversationHandler.END
    else:
        # Сообщаем пользователю, что номер заказа должен быть целым числом
        update.message.reply_text("Шаг 2/2. Номер заказа должен быть числом. \nНачните процесс заново нажав /delete")
        context.user_data['conversation'] = False
        return ConversationHandler.END
