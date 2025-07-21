"""
Panel functionality with inline keyboard for Docker Compose app management.
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.keyboards import get_main_keyboard
from glob import glob
from pathlib import Path
import os
import requests
import subprocess
import json
import time

logger = logging.getLogger(__name__)


async def get_app_status():
    """Scan for Docker Compose projects and get their status."""
    
    try:
        apps = requests.get(r'http://172.17.0.1:5000/apps').json()
        return apps
        
    except Exception as e:
        logger.error(f"Error scanning for apps: {e}")
        return []


async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /panel command - show main panel."""
    keyboard = [
        [InlineKeyboardButton("📊 App Status", callback_data="app_status")],
        [InlineKeyboardButton("❌ Close", callback_data="close_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎛️ **Docker Control Panel**\n\n"
        "Manage your Docker Compose applications:\n\n"
        "📊 **App Status** - View and control running apps\n"
        "❌ **Close** - Exit the panel",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def toggle_app_status(app_name: str) -> dict:
    """
    Toggle the status of a Docker Compose app.
    Returns dict with success status and new app status.
    """
   
    try:
        requests.post(rf'http://172.17.0.1:5000/toggle/{app_name}')
        return {'success': False, 'error': f'App {app_name} not found'}
        
    except Exception as e:
        logger.error(f"Error toggling app {app_name}: {e}")
        return {'success': False, 'error': str(e)}


def show_app_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all apps with their current status."""
    current_apps = get_app_status()
    
    if not current_apps:
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query = update.callback_query
        query.edit_message_text(
            "📭 **No Docker Compose Applications Found**\n\n"
            "No `docker-compose.yml` files found in subdirectories.\n"
            "Make sure your applications are in separate folders with their own docker-compose.yml files.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    keyboard = []
    status_summary = "📊 **Docker Applications Status**\n\n"
    
    for app_info in current_apps:
        status_text = "ON" if app_info['status'] else "OFF"
        status_emoji = "🟢" if app_info['status'] else "🔴"
        
        # Create button text with container count info
        if app_info['total_count'] > 0:
            button_text = f"{app_info['name']} ({app_info['running_count']}/{app_info['total_count']}) {status_emoji}"
        else:
            button_text = f"{app_info['name']} (No containers) ⚪"
        
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"toggle_{app_info['name']}")])
        
        # Add to status summary
        status_summary += f"{status_emoji} **{app_info['name']}**: {status_text}"
        if app_info['total_count'] > 0:
            status_summary += f" ({app_info['running_count']}/{app_info['total_count']} containers)"
        status_summary += "\n"
    
    # Add control buttons
    keyboard.append([
        InlineKeyboardButton("🔙 Back", callback_data="back_to_panel")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    status_summary += "**Click on any app to start/stop it**"
    
    query = update.callback_query
    await query.edit_message_text(
        status_summary,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def handle_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries from panel inline keyboards."""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback
    
    callback_data = query.data
    
    if callback_data == "app_status":
        show_app_status(update, context)
        
        
    elif callback_data == "close_panel":
        await query.edit_message_text(
            "🎛️ **Panel Closed**\n\n"
            "Use /panel command to open the control panel again."
        )
        
    elif callback_data == "back_to_panel":
        # Show main panel again
        keyboard = [
            [InlineKeyboardButton("📊 App Status", callback_data="app_status")],
            [InlineKeyboardButton("❌ Close", callback_data="close_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎛️ **Docker Control Panel**\n\n"
            "Manage your Docker Compose applications:\n\n"
            "📊 **App Status** - View and control running apps\n"
            "❌ **Close** - Exit the panel",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    elif callback_data.startswith("toggle_"):
        # Extract app name and toggle its status
        try:
            app_name = callback_data.replace("toggle_", "")
            toggle_app_status(app_name)
            time.sleep(5)
            show_app_status(update, context)
                
        except:
            # Show error message
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"**Error toggling {app_name}**",
                parse_mode='Markdown'
            )
            # Still refresh the status to show current state
            show_app_status(update, context)


# Additional utility functions for advanced features

async def get_app_logs(app_name: str, lines: int = 50) -> str:
    """Get recent logs for a specific app."""
    cwd = os.getcwd()
    
    try:
        for app in apps:
            if app['name'] == app_name:
                os.chdir(app['folder'])
                result = subprocess.run(
                    ['sudo', 'docker', 'compose', 'logs', '--tail', str(lines)],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return result.stdout
                else:
                    return f"Error getting logs: {result.stderr}"
        return f"App {app_name} not found"
    except Exception as e:
        logger.error(f"Error getting logs for {app_name}: {e}")
        return f"Error: {str(e)}"
    finally:
        os.chdir(cwd)


async def restart_app(app_name: str) -> dict:
    """Restart a Docker Compose app."""
    cwd = os.getcwd()
    
    try:
        for app in apps:
            if app['name'] == app_name:
                os.chdir(app['folder'])
                
                logger.info(f"Restarting app: {app_name}")
                result = subprocess.run(
                    ['sudo', 'docker', 'compose', 'restart'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    logger.info(f"Successfully restarted {app_name}")
                    return {'success': True, 'action': 'restarted'}
                else:
                    logger.error(f"Failed to restart {app_name}: {result.stderr}")
                    return {'success': False, 'error': result.stderr}
        
        return {'success': False, 'error': f'App {app_name} not found'}
        
    except Exception as e:
        logger.error(f"Error restarting app {app_name}: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        os.chdir(cwd)