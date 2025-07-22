"""
Main message handler that routes messages based on user state.
"""
from telegram import Update
from telegram.ext import ContextTypes
from utils.state_manager import state_manager
from handlers.basic_handlers import help_command, cancel_command
from handlers.url_shortener import shorten_command, handle_url_shortening, WAITING_FOR_URL
from handlers.web_monitor import handle_monit_message
from handlers.panel import panel_command
import os

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages."""
    user_id = update.effective_user.id
    user_message = update.message.text
    approve_ID = os.environ.get('APPROVE_ID', '').split(',')
    if user_id in approve_ID:
        
        # Handle keyboard button presses
        if user_message == "Shorten URL":
            await shorten_command(update, context)
            return
        elif user_message == "Help":
            await help_command(update, context)
            return
        elif user_message == "WebMonitor":
            await handle_monit_message(update)
            return
        elif user_message.lower() == "monit":
            await handle_monit_message(update)
            return
        elif user_message == "Panel":
            await panel_command(update, context)
            return
        elif user_message == "Cancel":
            await cancel_command(update, context)
            return
    
        # Check user state and route accordingly
        user_state = state_manager.get_state(user_id)
        
        if user_state == WAITING_FOR_URL:
            await handle_url_shortening(update, user_id, user_message)
        else:
        # Echo the message as default behavior
        await update.message.reply_text(user_message)
    else:
        await update.message.reply_text(user_message)