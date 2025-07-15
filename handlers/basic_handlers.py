"""
Basic command handlers for the bot.
"""
from telegram import Update
from telegram.ext import ContextTypes
from utils.keyboards import get_main_keyboard
from utils.state_manager import state_manager

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    reply_markup = get_main_keyboard()
    
    await update.message.reply_text(
        f'Hi {user.first_name}! Welcome to the multi-function bot! Use the buttons below to access different features.',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """Available Functions:

Commands:
/start - Start the bot and show keyboard buttons
/help - Show this help message
/shorten - Shorten a URL (or use the keyboard button)
/cancel - Cancel any active operation and return to main menu

Keyboard Buttons:
• Shorten URL - Tap this button, then send any URL to get a shortened version
• Help - Show this help message
• Cancel - Cancel any active operation and return to main menu

Echo Function:
Just send me any text message and I'll echo it back to you!

How to use URL Shortener:
1. Tap the "Shorten URL" button or use /shorten command
2. Send any valid URL (like https://example.com)
3. Get back a shortened URL using TinyURL service
4. Use "Cancel" button or /cancel command to exit URL shortening mode"""
    
    await update.message.reply_text(help_text)

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /cancel command to exit any waiting mode."""
    user_id = update.effective_user.id
    
    if state_manager.clear_state(user_id):
        reply_markup = get_main_keyboard()
        await update.message.reply_text(
            "Operation cancelled! You're back to the main menu.",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("No active operation to cancel.")