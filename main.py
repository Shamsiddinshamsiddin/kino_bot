import asyncio
import database
import handlers
import config
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    filters, 
    ConversationHandler
)

# Loggingni yoqamiz (xatolarni ko'rish uchun)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Botni global o'zgaruvchi sifatida e'lon qilamiz
application = None

async def init_bot():
    global application
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Conv Handler (Qisqartirilgan, o'zgarishsiz qoldiring)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add", handlers.admin_start), CommandHandler("delete", handlers.delete_movie_start)],
        states={
            handlers.CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_code)],
            handlers.FILE: [MessageHandler(filters.VIDEO | filters.Document.ALL, handlers.get_file)],
            handlers.NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_name)],
            handlers.DELETE_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.delete_movie_confirm)],
        },
        fallbacks=[CommandHandler("cancel", handlers.cancel)],
        per_message=False
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(handlers.button_handler))
    application.add_handler(CommandHandler("start", handlers.admin_panel))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.find_movie))
    
    await application.initialize()
    await application.bot.set_webhook(url=f"{config.WEBHOOK_URL}/webhook")

@app.route('/')
def home():
    return "Bot is running via Webhook!"

@app.route('/webhook', methods=['POST'])
def webhook():
    # Telegramdan kelgan update'ni qabul qilish
    update = Update.de_json(request.get_json(), application.bot)
    # Update'ni botga yuborish (async loop ichida)
    asyncio.run_coroutine_threadsafe(application.update_queue.put(update), asyncio.get_event_loop())
    return "OK", 200

if __name__ == '__main__':
    # Baza va botni ishga tushirish
    asyncio.run(database.init_db())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_bot())
    
    # Flask serverini ishga tushirish
    app.run(host="0.0.0.0", port=10000)