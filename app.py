import logging
import os
import json

from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 設定日誌 ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- 你的 Bot Token ---
# 建議從環境變數中獲取，安全性更高。
# 在 App Engine 上部署時，你會在 app.yaml 中設定 TELEGRAM_BOT_TOKEN。
# 在本地測試時，如果環境變數未設定，可以使用預設值 'YOUR_LOCAL_BOT_TOKEN_HERE'。
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_LOCAL_BOT_TOKEN_HERE")

if TOKEN == "YOUR_LOCAL_BOT_TOKEN_HERE":
    logger.warning("Bot Token 未設置環境變數 'TELEGRAM_BOT_TOKEN'，請確保在 App Engine 上設定或替換為你的實際 Token。")

# --- Flask 應用程式實例 ---
# App Engine 需要一個 Flask 或其他 WSGI 相容的應用程式實例來處理 HTTP 請求。
app = Flask(__name__)

# --- 初始化 python-telegram-bot Application ---
# 在 Webhook 模式下，我們不會直接呼叫 application.run_polling()。
# 相反，我們會手動將接收到的 Update 物件傳遞給 application.dispatcher。
application = Application.builder().token(TOKEN).build()

# --- Bot 功能定義 ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """處理 /start 命令"""
    user_name = update.effective_user.first_name if update.effective_user else "陌生人"
    await update.message.reply_text(f"哈囉 {user_name}！我是一個運行在 Google App Engine 上的 Telegram Bot。")
    logger.info(f"Received /start from {update.effective_user.id}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """回應用戶發送的任何文字訊息"""
    await update.message.reply_text(f"你說了：{update.message.text}")
    logger.info(f"Received message: {update.message.text} from {update.effective_user.id}")

# --- 註冊處理器 ---
# 將你的命令和訊息處理器加入到 application 的 dispatcher 中。
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# --- Webhook 端點 ---
# App Engine 會將 Telegram 的 Webhook POST 請求導向這個 URL。
# 路徑 '/telegram-webhook' 必須與 app.yaml 中的 handlers 配置一致。
@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    if request.method == "POST":
        # 從 POST 請求中獲取 JSON 數據
        update_json = request.get_json(force=True)
        
        if update_json:
            logger.info(f"Received webhook update: {update_json}")
            
            # 將 JSON 數據轉換為 telegram.Update 物件
            # 這個 Update 物件包含了所有的訊息、命令等資訊
            update = Update.de_json(update_json, application.bot)
            
            # 將 Update 物件傳遞給 Dispatcher 進行處理
            # run_once=True 確保 dispatcher 只處理這個特定的更新。
            application.dispatcher.process_update(update)
            
            # 返回 HTTP 200 OK 響應給 Telegram 伺服器
            # 這是必須的，告訴 Telegram 伺服器你已成功接收並處理了更新，避免重複發送。
            return jsonify({'status': 'ok'}), 200
        else:
            logger.warning("Received empty or invalid JSON from webhook.")
            return jsonify({'status': 'bad request'}), 400
    return jsonify({'status': 'method not allowed'}), 405

# --- App Engine 入口點 ---
# 當 Flask 應用程式在 App Engine 上運行時，Gunicorn (WSGI 伺服器) 會啟動它。
# 在本地測試時，你可以直接運行這個檔案。
if __name__ == '__main__':
    # 在本地運行時，通常使用 8080 端口，或由 PORT 環境變數指定。
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Flask 應用程式在本地啟動於端口 {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)