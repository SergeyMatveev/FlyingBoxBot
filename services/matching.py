import logging

from telegram import Update, Bot
from telegram.ext import ConversationHandler, CallbackContext

from constants import TOKEN
from database import find_matches, get_active_orders, connect_to_database, get_order_data

PREPARE_MATCHING, MATCHING = range(2)


def prepare_matching(update: Update, context: CallbackContext):
    logging.info(f"User {update.message.from_user.username} entered matching function.")

    # Если заказ идет по Каскаду событий после создания заявки, тогда берем на вход номер заказа с order_id

    if context.user_data.get('cascade') is not None:
        if context.user_data['cascade']:
            logging.info(f"User {update.message.from_user.username} entered cascade.")
            return matching(update, context)

    # Если вызов идет не из Каскада событий, а по запросу пользователя, тогда проверям сколько заказов у пользователя:
    # - если 1 то сразу метчинг запускаем
    # - если более 1 тогда спрашиваем какой номер
    # - если нет заказов, то говорим нет заказов

    username = update.message.from_user.username
    orders = get_active_orders(username)
    num_orders = len(orders)

    if num_orders == 1:
        last_order = orders[0]
        context.user_data['order_id'] = last_order[0]
        update.message.reply_text(f"Запускаем поиск совпадений по заказу №{last_order[0]},\n"
                                  f"Откуда: {last_order[2].capitalize()}\n"
                                  f"Куда: {last_order[3].capitalize()}\n"
                                  )
        return matching(update, context)
    elif num_orders > 1:
        update.message.reply_text(f"У вас несколько заказов:")
        for order in orders:
            created_at = order[7].strftime('%d.%m.%Y')
            update.message.reply_text(f"Заказ №{order[0]}, от {created_at}\n"
                                      f"Откуда: {order[2].capitalize()}\n"
                                      f"Куда: {order[3].capitalize()}\n"
                                      )
        update.message.reply_text("Введите номер заказа для поиска совпадений:")
        return MATCHING
    else:
        update.message.reply_text("У вас нет активных заказов. Опубликуйте посылку или перевозку в меню.")
        return ConversationHandler.END


def matching(update: Update, context: CallbackContext):
    context.user_data['order_id'] = int(context.user_data.get('order_id') or update.message.text)
    matches = find_matches(context.user_data['order_id'])

    if matches is None:
        # Обработка ошибки
        update.message.reply_text('Такого заказа нет.')
    elif matches is False:
        # Обработка ошибки
        update.message.reply_text('Произошла ошибка при поиске совпадений.')
    elif not matches:
        # Обработка случая, когда совпадений нет
        update.message.reply_text('На данный момент совпадений для этого маршрута не найдено.\nКак только появится подходящий курьер, Вам сразу придет сообщение.')

    else:
        if len(matches) > 5:
            update.message.reply_text(f'Показаны первые 5 совпадений из {len(matches)}.')
            orders_to_show = matches[:5]
        else:
            orders_to_show = matches

        for order in orders_to_show:
            created_at = order[7].strftime('%d.%m.%Y')
            send_date = order[5].strftime('%d.%m.%Y')

            if order[9]:
                message_text = (f"📦 Посылка №{order[0]} от {created_at}\n"
                                f"Кто: @{order[1]}\n"
                                f"Откуда: {order[2].capitalize()}\n"
                                f"Куда: {order[3].capitalize()}\n"
                                f"Вес: {float(order[4])} кг\n"
                                f"Желаемая дата отправки: {send_date}\n"
                                f"Комментарий: {order[6].capitalize()}\n")
            else:
                message_text = (f"✈️ Перевозка №{order[0]} от {created_at}\n"
                                f"Кто: @{order[1]}\n"
                                f"Откуда: {order[2].capitalize()}\n"
                                f"Куда: {order[3].capitalize()}\n"
                                f"Может взять: {float(order[4])} кг\n"
                                f"Дата поездки: {send_date}\n"
                                f"Комментарий: {order[6].capitalize()}\n")

            update.message.reply_text(message_text)

        update.message.reply_text('Совпадения найдены.\nСвяжитесь с пользователями для уточнения деталей.')
        if context.user_data.get('cascade') is not None:
            if context.user_data['cascade']:
                send_notification(update, context, matches)
                update.message.reply_text('Мы отправили уведомления о вашем заказе людям с подходящим маршрутом.')
    context.user_data['order_id'] = None
    return ConversationHandler.END


def send_notification(update, context, orders_to_notify):
    """
    Отправляет уведомления по списку заказов.
    """
    bot = Bot(TOKEN)
    order = get_order_data(context.user_data['order_id'])

    for order_to_notify in orders_to_notify:
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id FROM orders WHERE order_id = %s", (order_to_notify[0],))
            chat_id = cursor.fetchone()[0]

            if chat_id:
                message = f"Найдено совпадение по вашему маршруту. \nСвяжитесь с @{order[1]}.\nВот детали заказа."
                bot.send_message(chat_id, message)
                created_at = order[7].strftime('%d.%m.%Y')
                send_date = order[5].strftime('%d.%m.%Y')

                if order[9]:
                    message_text = (f"📦 Посылка №{order[0]} от {created_at}\n"
                                    f"Кто: @{order[1]}\n"
                                    f"Откуда: {order[2].capitalize()}\n"
                                    f"Куда: {order[3].capitalize()}\n"
                                    f"Вес: {float(order[4])} кг\n"
                                    f"Желаемая дата отправки: {send_date}\n"
                                    f"Комментарий: {order[6].capitalize()}\n")
                else:
                    message_text = (f"✈️ Перевозка №{order[0]} от {created_at}\n"
                                    f"Кто: @{order[1]}\n"
                                    f"Откуда: {order[2].capitalize()}\n"
                                    f"Куда: {order[3].capitalize()}\n"
                                    f"Может взять: {float(order[4])} кг\n"
                                    f"Дата поездки: {send_date}\n"
                                    f"Комментарий: {order[6].capitalize()}\n")

                bot.send_message(chat_id, message_text)

            cursor.close()
            context.user_data['cascade'] = False
        except Exception as error:
            print(error)
        finally:
            if conn:
                conn.close()
