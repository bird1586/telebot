"""
Web monitoring functionality for Telegram bot.
"""
from telegram import Update
from telegram.ext import ContextTypes
from utils.keyboards import get_main_keyboard

# Monitor URL
MONITOR_URL = "https://9bb6cac636e6.ngrok-free.app/"

async def webmonitor_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /webmonitor command."""
    reply_markup = get_main_keyboard()
    # chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"🌐 **Web Monitor**\n\nMonitoring URL: {MONITOR_URL}\n\n🔗 Click the link to access the monitoring dashboard.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_monit_message(update: Update) -> None:
    """Handle 'monit' message."""
    reply_markup = get_main_keyboard()
    await update.message.reply_text(
        f"🌐 **Web Monitor**\n\nMonitoring URL: {MONITOR_URL}\n\n🔗 Click the link to access the monitoring dashboard.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )