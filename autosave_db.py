import io
import logging
import pandas as pd
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import psycopg2

# Настройка логирования
logging.basicConfig(filename='autosave_db.log',
                    filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

DATABASE_NAME = 'postgres'
DATABASE_USER = 'postgres'
DATABASE_PASSWORD = 'postgres'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '5432'


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


# Функция для экспорта данных из таблицы в CSV и загрузки на Google Drive
def export_data_to_csv_and_upload(table_name):
    conn = connect_to_database()
    if conn is not None:
        try:
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
            current_date = datetime.now().strftime('%Y-%m-%d')
            filename = f"{table_name}_{current_date}.csv"

            csv_buffer = io.BytesIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8')
            csv_buffer.seek(0)

            credentials = service_account.Credentials.from_service_account_file(
                'sergey_google_account.json',
                scopes=['https://www.googleapis.com/auth/drive']
            )
            service = build('drive', 'v3', credentials=credentials)

            file_metadata = {
                'name': filename,
                'mimeType': 'text/csv',
                'parents': ['18iWsBXfaGjESM5cw4-1vVxcWS6ThzHyz']
            }
            media = MediaIoBaseUpload(csv_buffer, mimetype='text/csv', resumable=True)
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()

            logging.info(f"Файл {filename} успешно сохранён и загружен на Google Drive")
        except Exception as e:
            logging.error(f"Ошибка при работе с {table_name}: {e}")
        finally:
            conn.close()
    else:
        logging.error(f"Не удалось подключиться к базе данных для {table_name}")


# Основная логика скрипта
if __name__ == "__main__":
    export_data_to_csv_and_upload("orders")
    export_data_to_csv_and_upload("matches")
    logging.info("Matches were autosaved")
