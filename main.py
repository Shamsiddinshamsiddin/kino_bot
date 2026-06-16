import asyncio
import threading
import database
import handlers
import config
from flask import Flask
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    filters, 
    ConversationHandler
)

# Flask serveri (Render 24/7 ishlashi uchun)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host="0.0.0.0", port=10000)

async def main():
    # 1. Ma'lumotlar bazasini ishga tushirish
    await database.init_db()
    
    # 2. Botni sozlash
    application = Application.builder().token(config.BOT_TOKEN).build()

    # 3. ConversationHandler (Kino qo'shish va o'chirish jarayonlari)
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("add", handlers.admin_start),
            CommandHandler("delete", handlers.delete_movie_start)
        ],
        states={
            handlers.CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_code)],
            handlers.FILE: [MessageHandler(filters.VIDEO | filters.Document.ALL, handlers.get_file)],
            handlers.NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_name)],
            handlers.DELETE_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.delete_movie_confirm)],
        },
        fallbacks=[CommandHandler("cancel", handlers.cancel)],
        # per_message=False foydalanuvchiga barcha xabarlarini bitta jarayonda boshqarish imkonini beradi
        per_message=False 
    )

    # 4. Handlerlarni qo'shish
    # MUHIM: ConversationHandler birinchi bo'lishi kerak
    application.add_handler(conv_handler)
    
    # Tugmalar uchun handler
    application.add_handler(CallbackQueryHandler(handlers.button_handler))
    
    # Umumiy buyruqlar va xabarlar
    application.add_handler(CommandHandler("start", handlers.admin_panel))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.find_movie))

    print("Bot muvaffaqiyatli ishga tushdi...")
    
    # 5. Polling va Web-serverni ishga tushirish
    threading.Thread(target=run_web, daemon=True).start()
    
    # Botni ishga tushirish
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # Botni o'chirmasdan ushlab turish
    try:
        await asyncio.Event().wait()
    finally:
        await application.stop()
        await application.shutdown()

if __name__ == '__main__':
    asyncio.run(main())