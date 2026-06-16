from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import database
import config

# Holatlar (States)
CODE, FILE, NAME, DELETE_CODE = range(4)

# --- Admin Panel ---
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == int(config.ADMIN_ID):
        from keyboards import admin_menu
        await update.message.reply_text(
            "🛠 Admin paneliga xush kelibsiz!",
            reply_markup=admin_menu(),
        )
    else:
        await find_movie(update, context)

# --- Tugmalar (Callback Handler) ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "list_movies":
        movies = await database.get_all_movies()
        if not movies:
            await query.edit_message_text("❌ Hozircha kinolar mavjud emas.")
        else:
            text = "📋 Barcha kinolar:\n\n"
            for code, title in movies:
                text += f"🎬 {title} | Kod: `{code}`\n"
            await query.edit_message_text(text, parse_mode='Markdown')
    
    elif query.data == "add_movie":
        # Tugma bosilganda admin_start funksiyasiga yo'naltiramiz
        await admin_start(update, context)
        
    elif query.data == "delete_movie":
        await delete_movie_start(update, context)

# --- Kino qo'shish jarayoni ---
async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Agar callback orqali kelsa query, buyruq orqali kelsa message ishlatamiz
    text = "➕ Kino kodini kiriting:"
    if update.callback_query:
        await update.callback_query.message.reply_text(text)
    else:
        await update.message.reply_text(text)
    return CODE

async def get_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['code'] = update.message.text.strip().upper()
    await update.message.reply_text("Kino faylini (video/hujjat) yuboring:")
    return FILE

async def get_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.video.file_id if update.message.video else update.message.document.file_id
    context.user_data['file_id'] = file_id
    await update.message.reply_text("Kino nomini kiriting:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie_name = update.message.text.strip()
    code = context.user_data.get('code')
    file_id = context.user_data.get('file_id')

    await database.add_movie(code, movie_name, file_id)
    await update.message.reply_text(f"✅ {movie_name} muvaffaqiyatli qo'shildi!\nKod: {code}")
    context.user_data.clear()
    return ConversationHandler.END

# --- O'chirish jarayoni ---
async def delete_movie_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "➖ O'chirmoqchi bo'lgan kodni kiriting:"
    if update.callback_query:
        await update.callback_query.message.reply_text(text)
    else:
        await update.message.reply_text(text)
    return DELETE_CODE

async def delete_movie_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip().upper()
    await database.delete_movie(code)
    await update.message.reply_text(f"✅ {code}-kodli kino o'chirildi.")
    context.user_data.clear()
    return ConversationHandler.END

# --- Kino qidirish ---
async def find_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip().upper()
    movie = await database.get_movie(code)
    if movie:
        try:
            await update.message.reply_video(video=movie[2], caption=f"🎬 Kino: {movie[1]}")
        except:
            await update.message.reply_document(document=movie[2], caption=f"🎬 Kino: {movie[1]}")
    else:
        await update.message.reply_text("❌ Kino topilmadi. Kodni to'g'ri kiritganingizga ishonch hosil qiling.")

# --- Boshqalar ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Jarayon bekor qilindi.")
    context.user_data.clear()
    return ConversationHandler.END