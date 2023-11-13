import psycopg2
import logging
import io
from googleapiclient.http import MediaIoBaseUpload
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

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
            # Updated the INSERT statement to include the RETURNING clause
            insert_query = (
                "INSERT INTO Requests "
                "(username, city_from, city_to, weight, send_date, what_is_inside, created_at, is_completed, is_package) "
                "VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s) RETURNING request_id;"
            )
            cursor.execute(
                insert_query,
                (username, city_from, city_to, weight, send_date, what_is_inside, False, is_package)
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
    with conn.cursor() as cur:
        # Check if the order is already marked as completed
        cur.execute("SELECT is_completed FROM Requests WHERE username = %s AND request_id = %s;",
                    (username, order_number))
        result = cur.fetchone()
        if result and result[0]:
            # The order is already completed, so return False
            return False

        # If not completed, update the record to mark it as completed
        cur.execute("""
            UPDATE Requests
            SET is_completed = TRUE
            WHERE username = %s AND request_id = %s AND is_completed = FALSE;
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
        cur.execute("SELECT DISTINCT username FROM Requests;")
        unique_usernames = cur.fetchall()
        cur.close()
    conn.close()
    return unique_usernames


# Функция для получения данных из таблицы и сохранения их в CSV
def export_requests_to_csv_and_upload():
    # Подключение к базе данных
    conn = connect_to_database()
    # Запрос данных из таблицы requests
    df = pd.read_sql("SELECT * FROM requests", conn)
    conn.close()

    # Сохранение данных в CSV-файл в памяти как байтовый поток
    csv_buffer = io.BytesIO()
    df.to_csv(csv_buffer, index=False, encoding='utf-8')
    csv_buffer.seek(0)

    # Аутентификация в Google Drive API
    credentials = service_account.Credentials.from_service_account_file(
        'sergey_google_account.json',
        scopes=['https://www.googleapis.com/auth/drive']
    )
    service = build('drive', 'v3', credentials=credentials)

    # Загрузка файла на Google Drive
    file_metadata = {
        'name': 'requests.csv',
        'mimeType': 'text/csv',
        'parents': ['1fZDZfZK3eoTgsaRIuo-D889rcJbGM2QG']
    }
    media = MediaIoBaseUpload(csv_buffer, mimetype='text/csv', resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return True
