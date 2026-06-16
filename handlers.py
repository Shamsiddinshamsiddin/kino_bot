import database
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from keyboards import admin_menu
import config

# Holatlar (States)
CODE, FILE, NAME, DELETE_CODE, EDIT_NAME, EDIT_FILE = range(6)

# --- Admin Panel ---
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == int(config.ADMIN_ID):
        await update.message.reply_text(
            "🛠 Admin paneliga xush kelibsiz!\n\n"
            "Quyidagi tugmalar orqali kino qo'shish, o'chirish va tahrirlash mumkin.",
            reply_markup=admin_menu(),
        )
    else:
        await update.message.reply_text("🎬 Kinolar dunyosiga xush kelibsiz! Kodni yuboring, men uni topib beraman.")

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
        await query.edit_message_text("➕ Kino qo'shish uchun /add buyrug'ini yozing.")
    elif query.data == "delete_movie":
        await query.edit_message_text("➖ Kino o'chirish uchun /delete buyrug'ini yozing.")
    elif query.data == "edit_movie":
        await query.edit_message_text("✏️ Kino tahrirlash uchun /edit buyrug'ini yozing.")

# --- Kino qo'shish jarayoni ---
async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("➕ Kino qo'shish boshlandi. Kino kodini kiriting:")
    return CODE

async def get_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip().upper()
    context.user_data['code'] = code
    await update.message.reply_text("Kino faylini (video/hujjat) yuboring:")
    return FILE

async def get_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Faylni olish (video yoki document)
    file_id = update.message.video.file_id if update.message.video else update.message.document.file_id
    context.user_data['file_id'] = file_id
    await update.message.reply_text("Kino nomini kiriting:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie_name = update.message.text.strip()
    code = context.user_data.get('code')
    file_id = context.user_data.get('file_id')

    await database.add_movie(code, movie_name, file_id)
    await update.message.reply_text(f"✅ Muvaffaqiyatli qo'shildi!\nKod: {code}")
    context.user_data.clear()
    return ConversationHandler.END

# --- O'chirish va Tahrirlash ---
async def delete_movie_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("O'chirmoqchi bo'lgan kino kodini kiriting:")
    return DELETE_CODE

async def delete_movie_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip().upper()
    await database.delete_movie(code)
    await update.message.reply_text(f"✅ {code}-kodli kino o'chirildi.")
    context.user_data.clear()
    return ConversationHandler.END

async def find_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip().upper()
    movie = await database.get_movie(code)
    if movie:
        try:
            await update.message.reply_video(video=movie[2], caption=f"🎬 Kino: {movie[1]}")
        except:
            await update.message.reply_document(document=movie[2], caption=f"🎬 Kino: {movie[1]}")
    else:
        await update.message.reply_text("❌ Kino topilmadi.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Jarayon bekor qilindi.")
    context.user_data.clear()
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Yordam: /start, /add, /delete")