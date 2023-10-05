from telegram import Bot, Update
from telegram.ext import CallbackContext

from database import connect_to_database


def my_orders(update: Update, context: CallbackContext) -> None:
    # Получаем username
    username = update.callback_query.from_user.username

    # Получаем заказы пользователя из базы данных
    orders = get_user_orders(username)

    if not orders:
        update.callback_query.message.reply_text("У вас нет заказов.")
    else:
        message_text = "Ваши заказы:\n"
        for order in orders:
            created_at = order[9].strftime('%d-%m-%Y')  # Форматируем дату
            send_date = order[7].strftime('%d-%m-%Y')  # Форматируем дату
            message_text += (f"Номер заказа: {order[0]}\n "
                             f"Откуда: {order[2].capitalize()}, {order[3].capitalize()}\n "
                             f"Куда: {order[4].capitalize()}, {order[5].capitalize()}\n "
                             f"Вес: {order[6]}\n "
                             f"Что внутри: {order[8].capitalize()}\n "
                             f"Дата отправки: {send_date}\n "
                             f"Создан: {created_at}\n "
                             f"Статус: {'Завершен' if order[10] else 'В процессе'}\n\n")

        update.callback_query.message.reply_text(message_text)


def get_user_orders(username: str):
    conn = connect_to_database()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM Requests WHERE username = %s;", (username,))
        orders = cur.fetchall()
        cur.close()
    conn.close()
    return orders
