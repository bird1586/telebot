#!/usr/bin/env python3
"""
Webhook management utility for Telegram bot.
"""
import asyncio
import os
import sys
from telegram import Bot
from config import BOT_TOKEN

async def set_webhook(webhook_url: str, port: int = 8443):
    """Set webhook for the bot."""
    bot = Bot(token=BOT_TOKEN)
    
    full_webhook_url = f"{webhook_url}/{BOT_TOKEN}"
    
    try:
        result = await bot.set_webhook(
            url=full_webhook_url,
            allowed_updates=["message", "callback_query"]
        )
        
        if result:
            print(f"✅ Webhook set successfully!")
            print(f"📡 Webhook URL: {full_webhook_url}")
            print(f"🔌 Port: {port}")
        else:
            print("❌ Failed to set webhook")
            
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")

async def delete_webhook():
    """Delete webhook for the bot."""
    bot = Bot(token=BOT_TOKEN)
    
    try:
        result = await bot.delete_webhook()
        
        if result:
            print("✅ Webhook deleted successfully!")
            print("🔄 Bot will now use polling mode")
        else:
            print("❌ Failed to delete webhook")
            
    except Exception as e:
        print(f"❌ Error deleting webhook: {e}")

async def get_webhook_info():
    """Get current webhook information."""
    bot = Bot(token=BOT_TOKEN)
    
    try:
        webhook_info = await bot.get_webhook_info()
        
        print("📊 Current Webhook Info:")
        print(f"URL: {webhook_info.url or 'Not set'}")
        print(f"Has custom certificate: {webhook_info.has_custom_certificate}")
        print(f"Pending update count: {webhook_info.pending_update_count}")
        print(f"Last error date: {webhook_info.last_error_date or 'None'}")
        print(f"Last error message: {webhook_info.last_error_message or 'None'}")
        print(f"Max connections: {webhook_info.max_connections}")
        print(f"Allowed updates: {webhook_info.allowed_updates}")
        
    except Exception as e:
        print(f"❌ Error getting webhook info: {e}")

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python webhook_manager.py set <webhook_url> [port]")
        print("  python webhook_manager.py delete")
        print("  python webhook_manager.py info")
        print("\nExamples:")
        print("  python webhook_manager.py set https://your-domain.com")
        print("  python webhook_manager.py set https://abc123.ngrok-free.app 8443")
        print("  python webhook_manager.py delete")
        print("  python webhook_manager.py info")
        return

    command = sys.argv[1].lower()

    if command == "set":
        if len(sys.argv) < 3:
            print("❌ Please provide webhook URL")
            return
        
        webhook_url = sys.argv[2].rstrip('/')  # Remove trailing slash
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 8443
        
        asyncio.run(set_webhook(webhook_url, port))
        
    elif command == "delete":
        asyncio.run(delete_webhook())
        
    elif command == "info":
        asyncio.run(get_webhook_info())
        
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: set, delete, info")

if __name__ == "__main__":
    main()