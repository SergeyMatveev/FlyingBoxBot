from telegram import InlineKeyboardButton, InlineKeyboardMarkup

emoji_box = "\U0001F4E6"
emoji_plane = "\u2708"
emoji_book = "\U0001F4D6"
emoji_help = "\U0001F6DF"


def create_main_menu_buttons():
    button_send_package = InlineKeyboardButton(f"Отправить посылку {emoji_box}", callback_data="send_package")
    button_offer_courier_service = InlineKeyboardButton(f"Я готов перевезти {emoji_plane}",
                                                        callback_data="offer_courier_service")
    button_my_orders = InlineKeyboardButton(f"Заказы {emoji_book}", callback_data="my_orders")
    button_help = InlineKeyboardButton(f"Поддержка {emoji_help}", callback_data="request_support")

    keyboard = [[button_send_package], [button_offer_courier_service], [button_my_orders], [button_help]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


def create_language_buttons():
    keyboard = [
        [InlineKeyboardButton("English", callback_data='lang_en'),
         InlineKeyboardButton("Русский", callback_data='lang_ru')]
    ]
    return InlineKeyboardMarkup(keyboard)
