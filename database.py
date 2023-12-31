import psycopg2
import logging
import io
from googleapiclient.http import MediaIoBaseUpload
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

from constants import DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, MAX_DATE_DIFF

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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


def save_order_in_database(username, departure_city, destination_city, weight, departure_date, user_comment, is_package, chat_id):
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            # Updated the INSERT statement to include the RETURNING clause
            insert_query = (
                "INSERT INTO orders "
                "(username, departure_city, destination_city, weight, departure_date, user_comment, is_package, chat_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING order_id;"
            )
            cursor.execute(
                insert_query,
                (username, departure_city, destination_city, weight, departure_date, user_comment, is_package, chat_id)
            )
            # The RETURNING clause gives us the inserted ID
            order_id = cursor.fetchone()[0]
            conn.commit()

            cursor.close()
            conn.close()

            return order_id
        except Exception as e:
            logging.error(f"An error occurred while inserting your package request into the database: {e}")
            cursor.close()
            conn.close()
            return None
    else:
        return None


def get_active_orders(username: str):
    conn = connect_to_database()
    if conn is None:
        logging.error(f"An error occurred while connecting to database")
        return None
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM orders WHERE username = %s AND is_completed = FALSE;", (username,))
        orders = cur.fetchall()
        # Нет необходимости в явном вызове cur.close(), так как контекстный менеджер это сделает автоматически
    conn.close()
    return orders


def mark_order_as_completed(username: str, order_number: str) -> bool:
    conn = connect_to_database()
    with conn.cursor() as cur:
        # Check if the order is already marked as completed
        cur.execute("SELECT is_completed FROM orders WHERE username = %s AND order_id = %s;",
                    (username, order_number))
        result = cur.fetchone()
        if result and result[0]:
            # The order is already completed, so return False
            return False

        # If not completed, update the record to mark it as completed
        cur.execute("""
            UPDATE orders
            SET is_completed = TRUE
            WHERE username = %s AND order_id = %s AND is_completed = FALSE;
            """, (username, order_number))

        # Check if the row was updated
        if cur.rowcount > 0:
            conn.commit()
            return True
        else:
            return False


def get_unique_usernames():
    conn = connect_to_database()
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT username FROM orders;")
        unique_usernames = cur.fetchall()
        cur.close()
    conn.close()
    return unique_usernames


def get_order_data(order_id):
    """
    Получение данных заявки по ее ID.
    """
    try:
        with connect_to_database() as conn:
            with conn.cursor() as cur:
                query = "SELECT * FROM orders WHERE order_id = %s AND is_completed = FALSE"
                cur.execute(query, (order_id,))
                order_data = cur.fetchone()
                return order_data
    except Exception as e:
        logging.error(f"Error getting data: {e}")
        return None


def find_matches(order_id):
    """
    Поиск совпадающих заявок в базе данных.
    max_date_diff: Максимальная разница в датах (в днях).
    """

    order_data = get_order_data(order_id)
    if order_data is None:
        logging.info(f"Function find_matches returned False")
        return None  # Если заявка с таким ID не найдена

    order_id, username, departure_city, destination_city, weight, departure_date, user_comment, created_at, is_completed, is_package, chat_id = order_data

    if is_package:
        with connect_to_database() as conn:
            with conn.cursor() as cur:
                query = """
                SELECT * FROM orders
                WHERE departure_city = %s
                AND destination_city = %s
                AND is_package = False
                AND is_completed = False
                AND departure_date BETWEEN %s - INTERVAL '%s days' AND %s + INTERVAL '%s days'
                """
                cur.execute(query, (
                    departure_city, destination_city, departure_date, MAX_DATE_DIFF, departure_date,
                    MAX_DATE_DIFF))
                matches = cur.fetchall()
        return matches

    else:
        with connect_to_database() as conn:
            with conn.cursor() as cur:
                query = """
                SELECT * FROM orders
                WHERE departure_city = %s
                AND destination_city = %s
                AND is_package = True
                AND is_completed = False
                AND departure_date BETWEEN %s - INTERVAL '%s days' AND %s + INTERVAL '%s days'
                """
                cur.execute(query, (
                    departure_city, destination_city, departure_date, MAX_DATE_DIFF, departure_date,
                    MAX_DATE_DIFF))
                matches = cur.fetchall()
        return matches


def get_active_orders_count():
    # SQL-запрос для подсчёта активных заказов
    query = """
    SELECT COUNT(*)
    FROM orders
    WHERE is_completed = FALSE
    """

    # Установка соединения с базой данных
    connection = connect_to_database()
    cursor = connection.cursor()

    # Выполнение запроса и получение результата
    cursor.execute(query)
    active_orders_count = cursor.fetchone()[0]

    # Закрытие соединения с базой данных
    cursor.close()
    connection.close()

    return active_orders_count


def record_match(order_id, matched_order_id):
    try:
        with connect_to_database() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO matches (new_order_id, matched_order_id) VALUES (%s, %s)", (order_id, matched_order_id))
                conn.commit()
    except Exception as e:
        logging.error(f"Error in record_match: {e}")
