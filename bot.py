from datetime import datetime
import telegram
import firebase_admin
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler, CallbackContext
from firebase_admin import credentials, db
import os

# Define your Telegram Bot Token here
TOKEN = '6204132043:AAGsy6mKP485rFaBVGeeg6p1dSknDo76jlc'

# Get the current directory where your script is located
current_directory = os.getcwd()

# Define the file name or path relative to the current directory
file_name = "flyingbox-ab969-firebase-adminsdk-hv8ug-d802857247.json"

# Create the full file path by joining the current directory and file name
file_path = os.path.join(current_directory, file_name)

cred = credentials.Certificate(file_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://flyingbox-ab969-default-rtdb.europe-west1.firebasedatabase.app/'})


# Function to start the conversation
def start(update: telegram.Update, context: CallbackContext):
    update.message.reply_text("Скажи мне что-нибудь...")
    return ConversationHandler.END


# Function to echo the user's message
def echo_message(update: telegram.Update, context: CallbackContext):
    save_to_firebase(update)
    user_message = "хуе" + update.message.text
    update.message.reply_text(user_message)


# Function to save user input to Firebase
def save_to_firebase(update):
    # Extract user information and message from the update object
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    message = update.message.text

    # Create a unique timestamp for this message
    timestamp = int(datetime.now().timestamp() * 1000)  # Convert to milliseconds

    # Create a reference to a specific location in Firebase Realtime Database
    ref = db.reference(f'user_inputs/{user_id}/messages/{timestamp}')

    # Set data in the specified location as a dictionary
    ref.set({
        'username': username,
        'message': message,
        'timestamp': timestamp
    })


def main():
    # Initialize the Telegram Bot
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    # Define conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={},
        fallbacks=[],
    )

    dispatcher.add_handler(conv_handler)

    # Handle user messages with the echo_message function
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo_message))

    # Start the bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
