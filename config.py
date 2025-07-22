"""
Configuration settings for the Telegram bot.
"""
import os

# Bot configuration
BOT_TOKEN = os.getenv('TELEGRAM_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Webhook configuration
WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # Your public domain/ngrok URL
USE_WEBHOOK = os.getenv('USE_WEBHOOK', 'false').lower() == 'true'
PORT = int(os.getenv('PORT', 8443))

# Logging configuration
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOGGING_LEVEL = 'INFO'

# Bot settings
KEYBOARD_RESIZE = True
KEYBOARD_ONE_TIME = False
