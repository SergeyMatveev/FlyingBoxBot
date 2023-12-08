import logging
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from database import get_active_orders

SELECT_ORDER = 0


def my_orders(update: Update, context: CallbackContext) -> int:
    logging.info(f"User {update.message.from_user.username} entered my_orders function.")

    if 'conversation' in context.user_data and context.user_data['conversation']:
        logging.info(f"Error. User {update.message.from_user.username} tried to start new process without finishing previous.")
        update.message.reply_text(f"Вы уже находитесь в процессе создания заказа.\nЗакончите его или нажмите /cancel")
        return ConversationHandler.END
    context.user_data['conversation'] = True

    username = update.message.from_user.username
    orders = get_active_orders(username)

    if not orders:
        update.message.reply_text("У вас нет активных заказов. Опубликуйте посылку или перевозку в меню.")
        context.user_data['conversation'] = False
        return ConversationHandler.END
    else:
        for order in orders:
            created_at = order[7].strftime('%d.%m.%Y')
            send_date = order[5].strftime('%d.%m.%Y')

            # Добавляем условный оператор для order[11] - индикатор посылка или перевозка
            if order[9]:
                message_text = (f"📦 Ваша посылка №{order[0]} от {created_at}\n"
                                f"Откуда: {order[2].capitalize()}\n"
                                f"Куда: {order[3].capitalize()}\n"
                                f"Вес: {float(order[4])} кг\n"
                                f"Желаемая дата отправки: {send_date}\n"
                                f"Комментарий: {order[6].capitalize()}\n")
            else:
                message_text = (f"✈️ Ваша перевозка №{order[0]} от {created_at}\n"
                                f"Откуда: {order[2].capitalize()}\n"
                                f"Куда: {order[3].capitalize()}\n"
                                f"Готовы взять: {float(order[4])} кг\n"
                                f"Дата поездки: {send_date}\n"
                                f"Комментарий: {order[6].capitalize()}\n")

            update.message.reply_text(message_text)

        update.message.reply_text("Это список ваших активных заказов. \nДля удаления одного из заказов нажмите /delete")
        context.user_data['conversation'] = False
        return ConversationHandler.END

