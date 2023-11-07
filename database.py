import psycopg2
import logging
from constants import DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT

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


def user_exists(username):
    try:
        with connect_to_database() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT EXISTS (SELECT 1 FROM Users WHERE username = %s);", (username,))
                result = cursor.fetchone()
                return result[0]
    except Exception as e:
        logging.error(f"Ошибка проверки пользователя в базе данных: {e}")
        return False


def insert_user_into_database(username):
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Users (username, created_at) VALUES (%s, NOW());", (username,))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Ошибка добавления вашей учетной записи в базу данных: {e}")
            return False
    else:
        return False


def insert_request_into_database(username, city_from, city_to, weight, send_date, what_is_inside, is_package):
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Requests "
                "(username, city_from, city_to, weight, send_date, what_is_inside, created_at, is_completed, is_package) "
                "VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s);",
                (username, city_from, city_to, weight, send_date, what_is_inside, False, is_package)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Ошибка добавления вашей заявки на отправку посылки в базу данных: {e}")
            return False
    else:
        return False


def get_orders_by_countries(country_from: str, country_to: str):
    conn = connect_to_database()
    orders = []
    with conn.cursor() as cur:
        query = """SELECT * FROM Requests WHERE city_from = %s AND city_to = %s AND is_completed = FALSE;"""
        cur.execute(query, (country_from, country_to))
        orders = cur.fetchall()
    conn.close()
    return orders


def get_user_orders_filtered(username: str):
    conn = connect_to_database()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM Requests WHERE username = %s AND is_completed = FALSE;", (username,))
        orders = cur.fetchall()
        cur.close()
    conn.close()
    return orders


def mark_order_as_done(username: str, order_number: str) -> bool:
    conn = connect_to_database()
    is_successful = False
    with conn.cursor() as cur:
        cur.execute("UPDATE Requests SET is_completed = TRUE WHERE username = %s AND request_id = %s;",
                    (username, order_number))
        if cur.rowcount > 0:
            is_successful = True
        conn.commit()
        cur.close()
    conn.close()
    return is_successful
