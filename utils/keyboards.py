"""
Keyboard layouts for the Telegram bot.
"""
from telegram import KeyboardButton, ReplyKeyboardMarkup
from config import KEYBOARD_RESIZE, KEYBOARD_ONE_TIME

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Get the main menu keyboard."""
    keyboard = [
        [KeyboardButton("Shorten URL"), KeyboardButton("Help")],
        [KeyboardButton("WebMonitor"), KeyboardButton("Panel")],
        [KeyboardButton("Cancel")]
    ]
    return ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=KEYBOARD_RESIZE, 
        one_time_keyboard=KEYBOARD_ONE_TIME
    )

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Get a keyboard with just the cancel option."""
    keyboard = [
        [KeyboardButton("Cancel")]
    ]
    return ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=KEYBOARD_RESIZE, 
        one_time_keyboard=KEYBOARD_ONE_TIME
    )