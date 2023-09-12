from telegram.ext import Updater
from handlers import setup_handlers
from constants import TOKEN


def main():
    updater = Updater(token=TOKEN)
    setup_handlers(updater)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
