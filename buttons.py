from telegram import InlineKeyboardButton, InlineKeyboardMarkup

emoji_box = "\U0001F4E6"
emoji_plane = "\u2708"
emoji_book = "\U0001F4D6"
emoji_help = "\U0001F6DF"


def create_inline_buttons():
    button_send_package = InlineKeyboardButton(f"Send a package {emoji_box}", callback_data="send_package")
    button_offer_courier_service = InlineKeyboardButton(f"Offer courier service {emoji_plane}",
                                                        callback_data="offer_courier")
    button_my_orders = InlineKeyboardButton(f"My orders {emoji_book}", callback_data="send_package")
    button_help = InlineKeyboardButton(f"Help {emoji_help}", callback_data="offer_courier")

    keyboard = [[button_send_package], [button_offer_courier_service], [button_my_orders], [button_help]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup
