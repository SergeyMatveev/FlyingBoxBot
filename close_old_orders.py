#!/usr/bin/env python3
import logging
from datetime import datetime
import psycopg2

DATABASE_NAME = 'postgres'
DATABASE_USER = 'postgres'
DATABASE_PASSWORD = 'postgres'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '5432'


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


def update_completed_orders():
    """
    Обновление статуса is_completed в заказах, где текущая дата больше, чем departure_date.
    """
    try:
        with connect_to_database() as conn:
            with conn.cursor() as cur:
                # Получаем текущую дату
                current_date = datetime.now().date()

                # SQL-запрос для обновления статуса
                update_query = """
                UPDATE orders
                SET is_completed = TRUE
                WHERE departure_date < %s AND is_completed = FALSE
                """

                # Выполнение запроса
                cur.execute(update_query, (current_date,))

                # Фиксируем изменения в базе данных
                conn.commit()

                # Возвращаем количество обновленных записей
                logging.info(
                    f"Orders were updated because departure_date < current_date. Amount of rows affected: {cur.rowcount}")
                return cur.rowcount

    except Exception as e:
        logging.error(f"Error updating orders: {e}")
        return None


def main():
    try:
        updated_count = update_completed_orders()
        logging.info(f"Updated orders: {updated_count}")
    except Exception as e:
        logging.error(f"Error when closing old orders: {e}")


if __name__ == "__main__":
    main()
