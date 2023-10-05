import psycopg2
import logging
from constants import DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT
from datetime import date

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def connect_to_database():
    try:
        conn = psycopg2.connect(
            dbname=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST,
            port=DATABASE_PORT
        )
        return conn
    except Exception as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        return None


def user_exists(username):
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT EXISTS (SELECT 1 FROM Users WHERE username = %s);", (username,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result[0]
        except Exception as e:
            logging.error(f"Ошибка проверки пользователя в базе данных: {e}")
            return False
    else:
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


def update_user_language(username, language_code):
    conn = connect_to_database()
    if conn:
        try:
            logging.info(f"Executing UPDATE command with username: {username} and language_code: {language_code}")
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET language = %s WHERE username = %s;", (language_code, username))
            conn.commit()
            logging.info(f"Successfully executed UPDATE command for username: {username}")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error executing UPDATE command for username: {username}. Error: {e}")
            logging.error(f"Error updating user language in the database: {e}")
            return False
    else:
        return False


def insert_request_into_database(username, country_from, city_from, country_to, city_to, weight, send_date, what_is_inside):
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Requests "
                "(username, country_from, city_from, country_to, city_to, weight, send_date, what_is_inside, created_at, is_completed) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s);",
                (username, country_from, city_from, country_to, city_to, weight, send_date, what_is_inside, False)
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


def insert_route_into_database(username, origin_country, origin_city, destination_country, destination_city, comment):
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO Routes (user_id, origin_country, origin_city, destination_country, destination_city, comment)
                SELECT user_id, %s, %s, %s, %s, %s
                FROM Users WHERE username = %s;
                """,
                (origin_country, origin_city, destination_country, destination_city, comment, username)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Ошибка добавления вашей заявки на перевозку в базу данных: {e}")
            return False
    else:
        return False
