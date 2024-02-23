#!/usr/bin/env python3
import logging
import psycopg2
from telegram import Bot
from datetime import datetime

# Настройка логирования
log_filename = 'notify_orders_without_matches.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()  # Вывод логов в стандартный вывод
    ]
)

DATABASE_NAME = 'postgres'
DATABASE_USER = 'postgres'
DATABASE_PASSWORD = 'postgres'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '5432'
TOKEN = '6204132043:AAGsy6mKP485rFaBVGeeg6p1dSknDo76jlc'  # Замените на ваш токен бота

bot = Bot(TOKEN)


def connect_to_database():
    try:
        conn = psycopg2.connect(
            host=DATABASE_HOST,
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            port=DATABASE_PORT
        )
        return conn
    except Exception as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        return None


def fetch_orders_without_matches():
    """
    Выборка уникальных chat_id для заявок без совпадений.
    """
    try:
        with connect_to_database() as conn:
            with conn.cursor() as cur:
                # Измененный SQL-запрос для выборки уникальных chat_id заявок без метчей
                fetch_query = """
                SELECT DISTINCT o.chat_id
                FROM orders o
                LEFT JOIN matches m ON o.order_id = m.new_order_id
                WHERE o.is_completed = FALSE AND m.match_id IS NULL
                GROUP BY o.chat_id
                """

                # Выполнение запроса
                cur.execute(fetch_query)

                # Получение результатов
                unique_chat_ids = cur.fetchall()

                logging.info(f"Unique chat_ids without matches fetched: {len(unique_chat_ids)}")
                return unique_chat_ids

    except Exception as e:
        logging.error(f"Error fetching unique chat_ids without matches: {e}")
        return []


def notify_users(chat_ids):
    """
    Уведомление пользователей по уникальным chat_id.
    """
    for (chat_id,) in chat_ids:  # Распаковка кортежа с одним элементом
        message = "Здравствуйте, я продолжаю поиск подходящих заявок для вас. Пока не было совпадений, надеюсь появятся скоро."
        try:
            bot.send_message(chat_id, message)
            logging.info(f"Notification sent to chat_id {chat_id}")
        except Exception as e:
            logging.error(f"Failed to send message to chat_id {chat_id}: {e}")


def main():
    try:
        orders_without_matches = fetch_orders_without_matches()
        if orders_without_matches:
            notify_users(orders_without_matches)
        else:
            logging.info("No orders without matches to notify.")
    except Exception as e:
        logging.error(f"Error during notification process: {e}")


if __name__ == "__main__":
    main()
