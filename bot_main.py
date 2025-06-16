import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters
)
from qr_reader import read_qr
from parser import ReceiptParser
from cleaner import remove_file, move_to_archive
from exporter import append_cell_request
import json
from getter import get_json_data

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define states for ConversationHandler
WAITING_FOR_IMAGE = 1

# Handler for the /hello command
async def hello_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Hello, {update.effective_user.first_name}! 👋')

# Handler for the /start command, which shows the menu
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        [['/hello', '/add_receipt']],  # Added /add_receipt to menu
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await update.message.reply_text(
        "Welcome! Press a button below or type a command.",
        reply_markup=keyboard
    )

# Start the add_receipt conversation
async def add_receipt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Awaiting for QR code. Please send an image of the QR code, or /cancel to stop.")
    return WAITING_FOR_IMAGE

# Handle received images
async def qrcode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo
    if not photo:
        await update.message.reply_text("Please send an image of the QR code, or /cancel to stop.")
        return WAITING_FOR_IMAGE

    # Get the highest resolution photo
    file = await context.bot.get_file(photo[-1].file_id)
    # Ensure the folder exists
    os.makedirs("qr_codes", exist_ok=True)
    # Create a unique filename
    file_path = f"qr_codes/{update.effective_user.id}_{file.file_id}.jpg"
    await file.download_to_drive(file_path)
    await update.message.reply_text("QR code image received and saved. Thank you!")
    await update.message.reply_text("Processing the QR code...")
    receipt_link = read_qr(file_path)
    await update.message.reply_text("QR code processed successfully!")
    remove_file(file_path)  # Remove the file after processing
    if receipt_link:
        get_json_data(receipt_link)
        parser = ReceiptParser(receipt_link)
    else:
        await update.message.reply_text("No QR code found in the image.")
        return WAITING_FOR_IMAGE
    for file in os.listdir("parsed_data"):
        if file.endswith(".json"):
            parsed_file_path = os.path.join("parsed_data", file)
            with open(parsed_file_path, encoding="utf-8") as f:
                parsed_file = json.load(f)
            append_cell_request(parsed_file)
            move_to_archive(parsed_file_path)
    
        
        
    return ConversationHandler.END

# Handle non-image messages while waiting for image
async def non_qrcode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please send an image of the QR code, or /cancel to stop.")
    return WAITING_FOR_IMAGE

# Handle /cancel command
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("QR code upload cancelled.")
    return ConversationHandler.END

def main():
    BOT_TOKEN = ""

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Conversation handler for /add_receipt
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add_receipt", add_receipt_command)],
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
    app.add_handler(conv_handler)

    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()