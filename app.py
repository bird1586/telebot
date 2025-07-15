import os
import logging
import pyshorteners
import re
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.getenv('TELEGRAM_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Initialize URL shortener
shortener = pyshorteners.Shortener()

# Store user states for URL shortening
user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    
    # Create reply keyboard with function buttons
    keyboard = [
        [KeyboardButton("Shorten URL"), KeyboardButton("Help")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    await update.message.reply_text(
        f'Hi {user.first_name}! Welcome to the multi-function bot! Use the buttons below to access different features.',
        reply_markup=reply_markup
    )


async def show_help(update):
    """Show help message."""
    help_text = """Available Functions:

Commands:
/start - Start the bot and show keyboard buttons
/help - Show this help message
/shorten - Shorten a URL (or use the keyboard button)

Keyboard Buttons:
• Shorten URL - Tap this button, then send any URL to get a shortened version
• Help - Show this help message

Echo Function:
Just send me any text message and I'll echo it back to you!

How to use URL Shortener:
1. Tap the "Shorten URL" button or use /shorten command
2. Send any valid URL (like https://example.com)
3. Get back a shortened URL using TinyURL service"""
    
    await update.message.reply_text(help_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await show_help(update)

async def shorten_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /shorten command."""
    user_id = update.effective_user.id
    user_states[user_id] = 'waiting_for_url'
    await update.message.reply_text("Please send me a URL to shorten (e.g., https://example.com)")

def is_valid_url(url):
    """Check if the provided string is a valid URL."""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages."""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Handle keyboard button presses
    if user_message == "Shorten URL":
        user_states[user_id] = 'waiting_for_url'
        await update.message.reply_text("Please send me a URL to shorten (e.g., https://example.com)")
        return
    elif user_message == "Help":
        await show_help(update)
        return
    
    # Check if user is in URL shortening mode
    if user_id in user_states and user_states[user_id] == 'waiting_for_url':
        if is_valid_url(user_message):
            try:
                # Shorten the URL using TinyURL
                shortened_url = shortener.tinyurl.short(user_message)
                
                # Create keyboard to go back to main menu
                keyboard = [
                    [KeyboardButton("Shorten URL"), KeyboardButton("Help")]
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
                
                await update.message.reply_text(
                    f"Original URL: {user_message}\nShortened URL: {shortened_url}",
                    reply_markup=reply_markup
                )
                
                # Reset user state
                del user_states[user_id]
                
            except Exception as e:
                logger.error(f"Error shortening URL: {e}")
                await update.message.reply_text(
                    "Sorry, I couldn't shorten that URL. Please make sure it's a valid URL and try again."
                )
        else:
            await update.message.reply_text(
                "That doesn't look like a valid URL. Please send a URL starting with http:// or https://"
            )
    else:
        # Echo the message as before
        await update.message.reply_text(user_message)

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("shorten", shorten_command))
    
    # Register message handler for text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
