import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters
)

from assistant.qr_reader import read_qr
from assistant.parser import ReceiptParser
from assistant.cleaner import remove_file, move_to_archive
from assistant.exporter import (
    append_voucher_data,
    append_item_data,
    reset_sheets,
    prepare_sheets,
    initialize_tables,
)
from assistant.db_handler import (
    table_init,
    construct_user,
    add_googlesheet_key,
    join_googlesheet_key,
    get_user,
    GoogleSheetOwnershipError,
    GoogleSheetJoinError,
)
import json
from assistant.getter import get_json_data
from dotenv import load_dotenv
from assistant.config import TELEGRAM_BOT_TOKEN

# Load environment variables from a .env file if present
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define states for ConversationHandler
WAITING_FOR_IMAGE, WAITING_FOR_SHEET_KEY, WAITING_FOR_JOIN_SHEET_KEY = range(3)


def initialize_graphs(*args, **kwargs):
    """Placeholder hook for initializing dashboard graphs."""
    return None

def build_main_keyboard(user=None):
    """Return the appropriate keyboard for the user state."""
    buttons = ['/start']
    if user:
        if user.googlesheet_key:
            buttons.append('/scan_qrcode')
        else:
            buttons.extend(['/add_googlesheet', '/join_googlesheet'])

    return ReplyKeyboardMarkup(
        [buttons],
        resize_keyboard=True,
        one_time_keyboard=False,  # Persistent keyboard
    )


qr_keyboard = ReplyKeyboardMarkup(
    [['/cancel', '/scan_qrcode']],
    resize_keyboard=True,
    one_time_keyboard=False  # Persistent keyboard
)


# Handler for the /hello command
async def hello_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Hello, {update.effective_user.first_name}! 👋')

# Handler for the /start command, which shows the menu
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = construct_user(update.effective_user.id)
    if user:
        context.user_data["user"] = user
    await update.message.reply_text(
        "Welcome! Press a button below or type a command.",
        reply_markup=build_main_keyboard(user)
    )

# Start the scan_qr conversation
async def scan_qr_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Awaiting for QR code. Please send an image of the QR code, or /cancel to stop.",
                                    reply_markup=qr_keyboard)
    return WAITING_FOR_IMAGE

# Handle received images
async def qrcode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo
    if not photo:
        await update.message.reply_text("Please send an image of the QR code, or /cancel to stop.")
        return WAITING_FOR_IMAGE

    # Get the highest resolution photo
    file = await context.bot.get_file(photo[-1].file_id)
    raw_byte_array = await file.download_as_bytearray()
    await update.message.reply_text("Processing the QR code...")
    receipt_link = read_qr(raw_byte_array)
    if receipt_link:
        await update.message.reply_text("QR code found! Processing receipt...")
        logger.info("Received receipt link: %s", receipt_link)
        raw_data = get_json_data(receipt_link)
        user = context.user_data.get("user")
        if not user:
            await update.message.reply_text("Please run /start first to initialize your account.")
            return ConversationHandler.END
        parser = ReceiptParser(json_file=raw_data, user_telegram_id=user.user_id)
        if not parser.is_tax_id_new:
            await update.message.reply_text("This receipt has already been processed before.")
            return ConversationHandler.END
        else:
            parsed_json = parser.to_dict()
    else:
        await update.message.reply_text("No QR code found in the image, please try to send a clearer image.")
        return WAITING_FOR_IMAGE
    if parsed_json:
        if not user or not user.googlesheet_key:
            await update.message.reply_text(
                "No Google Sheet key found. Please set one using /add_googlesheet.",
            )
            return ConversationHandler.END
        append_item_data(user.googlesheet_key, parsed_json)
        append_voucher_data(user.googlesheet_key, parsed_json)
        await update.message.reply_text("QR code processed and data appended to Google Sheets!")

        
        
    return ConversationHandler.END

# Handle non-image messages while waiting for image
async def non_qrcode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please send an image of the QR code, or /cancel to stop.",
                                    reply_markup=qr_keyboard)
    return WAITING_FOR_IMAGE
    

# Handle /cancel command
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("QR code upload cancelled.",
                                    reply_markup=build_main_keyboard(context.user_data.get("user")))
    return ConversationHandler.END

# Handler for the /prepare_sheets command
async def prepare_sheet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Preparing sheets... Please wait.")
    user = context.user_data.get("user")
    if not user or not user.googlesheet_key:
        await update.message.reply_text(
            "No Google Sheet key found. Please set one using /add_googlesheet.",
            reply_markup=build_main_keyboard(user),
        )
        return
    try:
        reset_sheets(user.googlesheet_key)
        prepare_sheets(user.googlesheet_key)
        initialize_tables(user.googlesheet_key)
        # initialize_graphs(user.googlesheet_key) // her razberi etot syntax
        await update.message.reply_text(
            "Sheets have been reset and initialized successfully!",
            reply_markup=build_main_keyboard(user),
        )
    except Exception as e:
        logger.error(f"Error during sheet preparation: {e}")
        await update.message.reply_text(
            f"An error occurred: {e}",
            reply_markup=build_main_keyboard(user),
        )

# Handler for the /add_googlesheet command
async def add_google_sheet_key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt the user to provide a Google Sheet key."""
    user = context.user_data.get("user")
    if not user:
        await update.message.reply_text("Please run /start first to initialize your account.")
        return ConversationHandler.END

    await update.message.reply_text("Please do the following:"
                                    "1. Create a new Google Sheet"
                                    "2. Share it with personal-assistant@sheetsapi-460823.iam.gserviceaccount.com email. Make sure to provide Editor access."
                                    "3. Send the full link to the Google Sheet."
                                    "Waiting for your Google Sheet link...")
    return WAITING_FOR_SHEET_KEY


async def store_google_sheet_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store the Google Sheet key sent by the user."""
    user = context.user_data.get("user")
    if not user:
        await update.message.reply_text("Please run /start first to initialize your account.")
        return ConversationHandler.END

    raw_input = update.message.text.strip()
    try:
        key = add_googlesheet_key(user.user_id, raw_input)
    except GoogleSheetOwnershipError:
        await update.message.reply_text(
            "This Google Sheet key is already linked to another account. "
            "Please ask the current owner to release it or choose a different sheet."
        )
        return ConversationHandler.END

    user.googlesheet_key = key
    user.googlesheet_owner = 1

    try:
        reset_sheets(key)
        prepare_sheets(key)
        initialize_tables(key)
        #initialize_graphs(key)
    except Exception as e:
        logger.error(f"Error during sheet initialization: {e}")
        await update.message.reply_text(
            "Google Sheet key saved, but there was an error preparing the sheet."
            f" Please try again later or use /prepare_sheets.\nError: {e}",
            reply_markup=build_main_keyboard(user),
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Google Sheet key saved and sheets prepared!",
        reply_markup=build_main_keyboard(user),
    )
    return ConversationHandler.END


async def join_google_sheet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt the user to provide a Google Sheet key to join."""
    user = context.user_data.get("user")
    if not user:
        await update.message.reply_text("Please run /start first to initialize your account.")
        return ConversationHandler.END

    await update.message.reply_text("Please send a link to the Google Sheet you wish to join.")
    return WAITING_FOR_JOIN_SHEET_KEY


async def store_join_google_sheet_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store a Google Sheet key for a user joining an existing sheet."""
    user = context.user_data.get("user")
    if not user:
        await update.message.reply_text("Please run /start first to initialize your account.")
        return ConversationHandler.END

    raw_input = update.message.text.strip()
    try:
        key = join_googlesheet_key(user.user_id, raw_input)
    except GoogleSheetJoinError:
        await update.message.reply_text(
            "This Google Sheet key is not registered to any owner. Please ask the owner to add it first."
        )
        return ConversationHandler.END

    user.googlesheet_key = key
    if user.googlesheet_owner != 1:
        user.googlesheet_owner = 0
    await update.message.reply_text(
        "Joined Google Sheet successfully!",
        reply_markup=build_main_keyboard(user),
    )
    return ConversationHandler.END

# Handler for the /sheet_key command
async def sheet_key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the user's Google Sheet key back to them."""
    user = get_user(update.effective_user.id)

    if not user:
        await update.message.reply_text("Please run /start first to initialize your account.")
        return

    if user.googlesheet_key:
        await update.message.reply_text(f"Your Google Sheet key: {user.googlesheet_key}")
    else:
        await update.message.reply_text("No Google Sheet key found for your account.")

def main():
    BOT_TOKEN = TELEGRAM_BOT_TOKEN
    table_init()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Conversation handler for /scan_qrcode
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(["scan_qr", "scan_qrcode"], scan_qr_command)],
        states={
            WAITING_FOR_IMAGE: [
                MessageHandler(filters.PHOTO, qrcode_handler),
                MessageHandler(filters.COMMAND & filters.Regex('^/cancel$'), cancel_command),
                MessageHandler(filters.ALL, non_qrcode_handler),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("hello", hello_command))
    app.add_handler(CommandHandler("prepare_sheet", prepare_sheet_command))
    app.add_handler(CommandHandler("sheet_key", sheet_key_command))
    app.add_handler(conv_handler)
    sheet_key_conv_handler = ConversationHandler(
        entry_points=[CommandHandler(["add_google_sheet_key", "add_googlesheet"], add_google_sheet_key_command)],
        states={
            WAITING_FOR_SHEET_KEY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, store_google_sheet_key)
            ],
        },
        fallbacks=[],
    )
    app.add_handler(sheet_key_conv_handler)

    join_sheet_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("join_googlesheet", join_google_sheet_command)],
        states={
            WAITING_FOR_JOIN_SHEET_KEY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, store_join_google_sheet_key)
            ],
        },
        fallbacks=[],
    )
    app.add_handler(join_sheet_conv_handler)


    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
