"""
Basic command handlers for the Telegram bot.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.keyboards import get_main_keyboard
from utils.state_manager import state_manager

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    reply_markup = get_main_keyboard()
    
    welcome_message = (
        f"Hello {user.first_name}!\n\n"
        "Welcome to the Multi-Purpose Bot!\n\n"
        "I can help you with:\n"
        "- URL shortening\n"
        "- Web monitoring\n"
        "- Admin panel access\n\n"
        "Use the buttons below or type commands to get started!"
    )
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    reply_markup = get_main_keyboard()
    
    help_message = (
        "Bot Help\n\n"
        "Available Commands:\n"
        "• /start - Show main menu\n"
        "• /help - Show this help\n"
        "• /shorten - Shorten URLs\n"
        "• /webmonitor - Web monitoring\n"
        "• /panel - Admin control panel\n"
        "• /cancel - Cancel operation\n\n"
        "Quick Tips:\n"
        "• Use keyboard buttons for navigation\n"
        "• Type 'monit' for quick monitoring\n"
        "• Cancel button exits any operation"
    )
    
    await update.message.reply_text(
        help_message,
        reply_markup=reply_markup
    )

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /cancel command."""
    user_id = update.effective_user.id
    reply_markup = get_main_keyboard()
    
    # Clear any active user state
    if state_manager.has_state(user_id):
        state_manager.clear_state(user_id)
        message = "Operation cancelled. You're back to the main menu."
    else:
        message = "No active operation to cancel. You're already at the main menu."
    
    await update.message.reply_text(
        message,
        reply_markup=reply_markup
    )