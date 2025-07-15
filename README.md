# Telegram Multi-Function Bot

A modular Telegram bot with URL shortening functionality and extensible architecture.

## Features

- **URL Shortening**: Shorten URLs using TinyURL service
- **Cancel Operations**: Exit any waiting mode with cancel command/button
- **Echo Function**: Echo back any text messages
- **Modular Architecture**: Easy to extend with new features

## Project Structure

```
├── app.py                    # Main application entry point
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── handlers/                 # Message and command handlers
│   ├── __init__.py
│   ├── basic_handlers.py     # Start, help, cancel commands
│   ├── url_shortener.py      # URL shortening functionality
│   └── message_handler.py    # Main message router
└── utils/                    # Utility modules
    ├── __init__.py
    ├── keyboards.py          # Telegram keyboard layouts
    ├── state_manager.py      # User state management
    └── validators.py         # Input validation utilities
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your bot token:
   ```bash
   export TELEGRAM_TOKEN="your_bot_token_here"
   ```

3. Run the bot:
   ```bash
   python app.py
   ```

## Adding New Features

1. Create a new handler file in `handlers/`
2. Define your state constants and handler functions
3. Add state handling logic in `message_handler.py`
4. Register commands in `app.py`
5. Update keyboards in `utils/keyboards.py` if needed

## Commands

- `/start` - Start the bot and show main menu
- `/help` - Show help message
- `/shorten` - Enter URL shortening mode
- `/cancel` - Cancel any active operation

## Architecture Benefits

- **Separation of Concerns**: Each module has a specific responsibility
- **Easy Testing**: Individual components can be tested in isolation
- **Scalability**: New features can be added without modifying existing code
- **Maintainability**: Clear structure makes debugging and updates easier