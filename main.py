import asyncio
import database
import handlers
import config
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler

async def main():
    await database.init_db()
    application = Application.builder().token(config.BOT_TOKEN).build()

    # ConversationHandler - faqat ketma-ket jarayonlar uchun
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("add", handlers.admin_start),
            CommandHandler("delete", handlers.delete_movie_start)
        ],
        states={
            handlers.CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_code)],
            handlers.FILE: [MessageHandler(filters.VIDEO | filters.Document.ALL, handlers.get_file)],
            handlers.EDIT_NAME: [MessageHandler(filters.VIDEO | filters.Document.ALL, handlers.get_edit_file)],
            handlers.DELETE_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.delete_movie_confirm)],
            handlers.EDIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_edit_name)],
            handlers.EDIT_FILE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_edit_file)],
        },
        fallbacks=[CommandHandler("cancel", handlers.cancel)],
        per_message=False
    )

    # Handlerlarni qo'shish
    application.add_handler(conv_handler)
    
    # Tugmalar uchun handler (Konversiyadan tashqarida)
    application.add_handler(CallbackQueryHandler(handlers.button_handler))
    
    # Asosiy buyruqlar
    application.add_handler(CommandHandler("start", handlers.admin_panel))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.find_movie))

    print("Bot muvaffaqiyatli ishga tushdi...")
    
    # Polling boshlash
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    try:
        await asyncio.Event().wait()
    finally:
        await application.stop()
        await application.shutdown()

if __name__ == '__main__':
    asyncio.run(main())