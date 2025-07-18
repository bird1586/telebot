"""
Configuration settings for the Telegram bot.
"""
import os

# Bot configuration
BOT_TOKEN = open('.env', 'r').read().strip() 

# Logging configuration
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOGGING_LEVEL = 'INFO'

# Bot settings
KEYBOARD_RESIZE = True
KEYBOARD_ONE_TIME = False
