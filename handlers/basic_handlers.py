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
    help_text = """🤖 **Available Commands:**

/start - Show main menu
/help - Show this help
/shorten - Shorten a URL
/cancel - Cancel current operation

💡 **Tip:** Use the keyboard buttons for easier access!"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

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