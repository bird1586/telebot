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
import subprocess
import json

logger = logging.getLogger(__name__)

# Global apps list
apps = []


def get_compose_ps_info(compose_dir='.'):
    """Get Docker Compose container status information."""
    cmd = ['sudo', 'docker', 'compose', 'ps', '--format', 'json']
    try:
        result = subprocess.run(
            cmd,
            cwd=compose_dir,
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        if not output:
            return []
        
        # Parse JSON output - each line is a separate JSON object
        containers = []
        for line in output.split('\n'):
            if line.strip():
                try:
                    container_info = json.loads(line)
                    containers.append(container_info)
                except json.JSONDecodeError:
                    continue
        return containers
    except subprocess.CalledProcessError as e:
        logger.error(f"Docker compose ps failed: {e}")
        return []
    except Exception as e:
        logger.error(f"Error getting compose info: {e}")
        return []


async def get_app_status():
    """Scan for Docker Compose projects and get their status."""
    global apps
    apps = []  # Reset apps list
    cwd = os.getcwd()
    
    try:
        # Find all docker-compose.yml files in subdirectories
        files = glob('*/docker-compose.yml')
        
        for file in files:
            path = Path(file)
            project_path = os.path.join(cwd, path.parent)
            
            # Change to project directory to run docker compose commands
            os.chdir(project_path)
            
            # Get container status
            containers = get_compose_ps_info()
            
            # Check if any containers are running
            running_containers = [c for c in containers if c.get('State') == 'running']
            
            app_info = {
                'name': path.parent.name,
                'status': len(running_containers) > 0,
                'folder': project_path,
                'containers': containers,
                'running_count': len(running_containers),
                'total_count': len(containers)
            }
            
            apps.append(app_info)
            logger.info(f"Found app: {app_info['name']} - Status: {'Running' if app_info['status'] else 'Stopped'}")
        
        # Return to original directory
        os.chdir(cwd)
        return apps
        
    except Exception as e:
        logger.error(f"Error scanning for apps: {e}")
        os.chdir(cwd)  # Ensure we return to original directory
        return []


async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /panel command - show main panel."""
    keyboard = [
        [InlineKeyboardButton("📊 App Status", callback_data="app_status")],
        [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_apps")],
        [InlineKeyboardButton("❌ Close", callback_data="close_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎛️ **Docker Control Panel**\n\n"
        "Manage your Docker Compose applications:\n\n"
        "📊 **App Status** - View and control running apps\n"
        "🔄 **Refresh** - Scan for new applications\n"
        "❌ **Close** - Exit the panel",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def toggle_app_status(app_name: str) -> dict:
    """
    Toggle the status of a Docker Compose app.
    Returns dict with success status and new app status.
    """
    cwd = os.getcwd()
    
    try:
        for app in apps:
            if app['name'] == app_name:
                os.chdir(app['folder'])
                
                if app['status']:  # Currently running - stop it
                    logger.info(f"Stopping app: {app_name}")
                    result = subprocess.run(
                        ['sudo', 'docker', 'compose', 'down'],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        app['status'] = False
                        logger.info(f"Successfully stopped {app_name}")
                        return {'success': True, 'new_status': False, 'action': 'stopped'}
                    else:
                        logger.error(f"Failed to stop {app_name}: {result.stderr}")
                        return {'success': False, 'error': result.stderr}
                        
                else:  # Currently stopped - start it
                    logger.info(f"Starting app: {app_name}")
                    result = subprocess.run(
                        ['sudo', 'docker', 'compose', 'up', '-d'],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        app['status'] = True
                        logger.info(f"Successfully started {app_name}")
                        return {'success': True, 'new_status': True, 'action': 'started'}
                    else:
                        logger.error(f"Failed to start {app_name}: {result.stderr}")
                        return {'success': False, 'error': result.stderr}
        
        return {'success': False, 'error': f'App {app_name} not found'}
        
    except Exception as e:
        logger.error(f"Error toggling app {app_name}: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        os.chdir(cwd)


async def show_app_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all apps with their current status."""
    current_apps = await get_app_status()
    
    if not current_apps:
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query = update.callback_query
        await query.edit_message_text(
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
        InlineKeyboardButton("🔄 Refresh", callback_data="refresh_apps"),
        InlineKeyboardButton("🔙 Back", callback_data="back_to_panel")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    status_summary += "\n💡 **Click on any app to start/stop it**\n🔄 **Refresh** to update status"
    
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
        await show_app_status(update, context)
        
    elif callback_data == "refresh_apps":
        # Refresh app list and show status
        await query.answer("🔄 Refreshing applications...")
        await show_app_status(update, context)
        
    elif callback_data == "close_panel":
        await query.edit_message_text(
            "🎛️ **Panel Closed**\n\n"
            "Use /panel command to open the control panel again."
        )
        
    elif callback_data == "back_to_panel":
        # Show main panel again
        keyboard = [
            [InlineKeyboardButton("📊 App Status", callback_data="app_status")],
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_apps")],
            [InlineKeyboardButton("❌ Close", callback_data="close_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎛️ **Docker Control Panel**\n\n"
            "Manage your Docker Compose applications:\n\n"
            "📊 **App Status** - View and control running apps\n"
            "🔄 **Refresh** - Scan for new applications\n"
            "❌ **Close** - Exit the panel",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    elif callback_data.startswith("toggle_"):
        # Extract app name and toggle its status
        app_name = callback_data.replace("toggle_", "")
        
        # Show loading message
        await query.answer(f"🔄 Toggling {app_name}...")
        
        # Toggle the app status
        result = await toggle_app_status(app_name)
        
        if result['success']:
            # Show updated status
            await show_app_status(update, context)
            
            # Send notification about the status change
            action_emoji = "✅" if result['new_status'] else "⏹️"
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"{action_emoji} **{app_name.replace('_', ' ').title()}** has been {result['action']}!"
            )
        else:
            # Show error message
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"❌ **Error toggling {app_name}:**\n```\n{result.get('error', 'Unknown error')}\n```",
                parse_mode='Markdown'
            )
            # Still refresh the status to show current state
            await show_app_status(update, context)


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