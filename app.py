"""
Main bot application entry point.
"""
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import BOT_TOKEN, LOGGING_FORMAT, LOGGING_LEVEL
from handlers.basic_handlers import start, help_command, cancel_command
from handlers.url_shortener import shorten_command
from handlers.web_monitor import webmonitor_command
from handlers.panel import panel_command, handle_panel_callback
from handlers.message_handler import handle_message

# Enable logging
logging.basicConfig(
    format=LOGGING_FORMAT,
    level=getattr(logging, LOGGING_LEVEL)
)
logger = logging.getLogger(__name__)

def setup_handlers(application: Application) -> None:
    """Set up all command and message handlers."""
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("shorten", shorten_command))
    application.add_handler(CommandHandler("webmonitor", webmonitor_command))
    application.add_handler(CommandHandler("panel", panel_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    
    # Callback query handler for inline keyboards
    application.add_handler(CallbackQueryHandler(handle_panel_callback))
    
    # Message handler for text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Setup handlers
    setup_handlers(application)
    
    # Run the bot until the user presses Ctrl-C
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()