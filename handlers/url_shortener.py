"""
URL shortening functionality.
"""
import logging
import pyshorteners
from telegram import Update
from telegram.ext import ContextTypes
from utils.keyboards import get_main_keyboard
from utils.state_manager import state_manager
from utils.validators import is_valid_url

# Initialize logger and URL shortener
logger = logging.getLogger(__name__)
shortener = pyshorteners.Shortener()

# State constants
WAITING_FOR_URL = 'waiting_for_url'

async def shorten_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /shorten command."""
    user_id = update.effective_user.id
    state_manager.set_state(user_id, WAITING_FOR_URL)
    await update.message.reply_text(
        "Please send me a URL to shorten (e.g., https://example.com)\n\n"
        "Tip: Use the 'Cancel' button or type /cancel to exit this mode."
    )

async def handle_url_shortening(update: Update, user_id: int, url: str) -> None:
    """Handle URL shortening process."""
    if is_valid_url(url):
        try:
            # Shorten the URL using TinyURL
            shortened_url = shortener.tinyurl.short(url)
            
            # Create keyboard to go back to main menu
            reply_markup = get_main_keyboard()
            
            await update.message.reply_text(
                f"Original URL: {url}\nShortened URL: {shortened_url}",
                reply_markup=reply_markup
            )
            
            # Reset user state
            state_manager.clear_state(user_id)
            
        except Exception as e:
            logger.error(f"Error shortening URL: {e}")
            await update.message.reply_text(
                "Sorry, I couldn't shorten that URL. Please make sure it's a valid URL and try again."
            )
    else:
        await update.message.reply_text(
            "That doesn't look like a valid URL. Please send a URL starting with http:// or https://"
        )