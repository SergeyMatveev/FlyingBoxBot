#!/usr/bin/env python3
import logging
import psycopg2
from telegram import Bot
from datetime import datetime

# Настройка логирования
log_filename = 'send_travel_wishes.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

DATABASE_NAME = 'postgres'
DATABASE_USER = 'postgres'
DATABASE_PASSWORD = 'postgres'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '5432'
TOKEN = '6204132043:AAGsy6mKP485rFaBVGeeg6p1dSknDo76jlc'

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

def fetch_today_non_package_orders():
    """
    Выборка заказов, где is_package == False и departure_date == today.
    """
    today = datetime.now().date()
    try:
        with connect_to_database() as conn:
            with conn.cursor() as cur:
                fetch_query = """
                SELECT chat_id
                FROM orders
                WHERE is_package = FALSE AND departure_date = %s
                """

                cur.execute(fetch_query, (today,))

                chat_ids = cur.fetchall()

                logging.info(f"Non-package orders with today's departure date fetched: {len(chat_ids)}")
                return chat_ids

    except Exception as e:
        logging.error(f"Error fetching today's non-package orders: {e}")
        return []

def send_travel_wishes(chat_ids):
    """
    Отправка пожеланий приятной поездки.
    """
    for (chat_id,) in chat_ids:
        message = "Желаем вам приятной поездки сегодня!"
        try:
            bot.send_message(chat_id, message)
            logging.info(f"Travel wish sent to chat_id {chat_id}")
        except Exception as e:
            logging.error(f"Failed to send travel wish to chat_id {chat_id}: {e}")

def main():
    try:
        chat_ids = fetch_today_non_package_orders()
        if chat_ids:
            send_travel_wishes(chat_ids)
        else:
            logging.info("No non-package orders with today's departure date to send wishes.")
    except Exception as e:
        logging.error(f"Error during sending travel wishes: {e}")

if __name__ == "__main__":
    main()
