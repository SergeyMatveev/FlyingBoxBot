import logging
from logging.handlers import SysLogHandler
from telegram.ext import Updater
from handlers import setup_handlers
from constants import TOKEN

# Настройка логирования
logging.basicConfig(level=logging.INFO)
syslog = SysLogHandler()
syslog.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
syslog.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(syslog)


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
