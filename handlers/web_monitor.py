"""
Web monitoring functionality for Telegram bot.
"""
from telegram import Update
from telegram.ext import ContextTypes
from utils.keyboards import get_main_keyboard
import requests

# Monitor URL
def get_url():
    tunnels = requests.get('http://172.17.0.1:4040/api/tunnels').json()
    telebot_url = "Not found"
    for tunnel in tunnels:
        if tunnel['name'] == 'changeDetection':
            telebot_url = tunnel['public_url']
    return telebot_url


async def webmonitor_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /webmonitor command."""
    reply_markup = get_main_keyboard()
    MONITOR_URL = get_url()
    # chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"🌐 **Web Monitor**\n\nMonitoring URL: {MONITOR_URL}\n\n🔗 Click the link to access the monitoring dashboard.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_monit_message(update: Update) -> None:
    """Handle 'monit' message."""
    reply_markup = get_main_keyboard()
    MONITOR_URL = get_url()
    await update.message.reply_text(
        f"🌐 **Web Monitor**\n\nMonitoring URL: {MONITOR_URL}\n\n🔗 Click the link to access the monitoring dashboard.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )