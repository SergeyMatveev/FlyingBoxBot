#!/usr/bin/env python3
import logging
from datetime import date
import psycopg2
import telegram

# Укажите здесь токен вашего бота
BOT_TOKEN = '6204132043:AAGsy6mKP485rFaBVGeeg6p1dSknDo76jlc'

GROUP_CHAT_ID = '-1001837659021'

# Настройка логирования
log_filename = 'flyingbox_daily_metrics.log'
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

# Создание экземпляра бота
bot = telegram.Bot(BOT_TOKEN)


def connect_to_database():
    try:
        return psycopg2.connect(
            host=DATABASE_HOST,
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            port=DATABASE_PORT
        )
    except Exception as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        return None


def get_active_orders_count():
    try:
        with connect_to_database() as conn:
            with conn.cursor() as cur:
                query = "SELECT COUNT(*) FROM orders WHERE is_completed = FALSE"
                cur.execute(query)
                active_orders_count = cur.fetchone()[0]
                return active_orders_count
    except Exception as e:
        logging.error(f"Error in get_active_orders_count: {e}")
        raise


def get_recent_orders_count():
    try:
        with connect_to_database() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT COUNT(*)
                    FROM orders
                    WHERE created_at > NOW() - INTERVAL '24 HOURS'
                    """
                cur.execute(query)
                recent_orders_count = cur.fetchone()[0]
                return recent_orders_count
    except Exception as e:
        logging.error(f"Error in get_recent_orders_count: {e}")
        raise


def get_recent_matches_count():
    try:
        with connect_to_database() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT COUNT(*)
                    FROM matches
                    WHERE match_time > NOW() - INTERVAL '24 HOURS'
                    """
                cur.execute(query)
                recent_matches_count = cur.fetchone()[0]
                return recent_matches_count
    except Exception as e:
        logging.error(f"Error in get_recent_matches_count: {e}")
        raise


def forward_to_group(active_orders_count, recent_orders_count, recent_matches_count):
    today = date.today().strftime('%d.%m.%Y')
    message = (f"Отчёт на {today}:\n"
               f"Количество активных заказов: {active_orders_count}\n"
               f"Заказов добавлено за последние сутки: {recent_orders_count}\n"
               f"Совпадений за последние сутки: {recent_matches_count}")
    bot.send_message(GROUP_CHAT_ID, message)


def main():
    try:
        active_orders_count = get_active_orders_count()
        recent_orders_count = get_recent_orders_count()
        recent_matches_count = get_recent_matches_count()

        forward_to_group(active_orders_count, recent_orders_count, recent_matches_count)

        logging.info(f"Daily metrics sent. Active orders count: {active_orders_count}, "
                     f"Orders added in last 24 hours: {recent_orders_count}, "
                     f"Matches in last 24 hours: {recent_matches_count}")
    except Exception as e:
        logging.error(f"Error when making daily metrics: {e}")


if __name__ == "__main__":
    main()
