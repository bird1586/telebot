"""
Simple test script that sends a hello message and exits.
"""
import asyncio
from telegram import Bot, constants
import requests

async def send_hello():
    """Send a hello message to a chat and exit."""
    bot = Bot(token='7867302269:AAEBkaBgk5Hck8Hlut9Uw7I2N9mcddkVQ1I')
    
    # You need to replace this with your chat ID or username
    # To get your chat ID, message the bot first, then check bot logs
    chat_id = "8044026942"  # Replace with actual chat ID
    
    res = requests.get('https://ask-english-785736210439.us-central1.run.app')
    
    try:
        # await bot.message.reply_text(res.text, chat_id=chat_id,reply_markup=reply_keyboard, parse_mode=ParseMode.MARKDOWN_V2)
        await bot.send_message(chat_id=chat_id, text=res.text, parse_mode=constants.ParseMode.MARKDOWN)
        print("Message sent successfully!")
    except Exception as e:
        print(f"Error sending message: {e}")
        print("Make sure to replace 'YOUR_CHAT_ID_HERE' with your actual chat ID")

if __name__ == '__main__':
    asyncio.run(send_hello())