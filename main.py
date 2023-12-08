import logging
from logging.handlers import SysLogHandler
from telegram.ext import Updater
from handlers import setup_handlers
from constants import TOKEN
from datetime import datetime

# Настройка формата даты для имени файла лога
current_date = datetime.now().strftime("%Y_%m_%d")
log_filename = f"flyingboxbot_log_{current_date}.log"

# Настройка формата сообщений лога
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Настройка логирования
logging.basicConfig(level=logging.INFO, format=log_format)

# Настройка SysLogHandler
syslog = SysLogHandler()
syslog.setLevel(logging.INFO)
syslog.setFormatter(logging.Formatter(log_format))
root_logger = logging.getLogger()
root_logger.addHandler(syslog)

# Настройка FileHandler для логирования в файл с датой в названии
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(log_format))
root_logger.addHandler(file_handler)


def main():
    updater = Updater(token=TOKEN)
    setup_handlers(updater)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    # Логирование при старте бота
    logging.info("Starting bot...")
    try:
        main()
    except Exception as e:
        logging.exception("Unexpected error occurred: %s", e)
