from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def admin_menu():
    keyboard = [
        [InlineKeyboardButton("➕ Kino qo'shish", callback_data="add_movie")],
        [InlineKeyboardButton("➖ Kino o'chirish", callback_data="delete_movie")],
        [InlineKeyboardButton("📋 Barcha kinolar", callback_data="list_movies")],
        [InlineKeyboardButton("✏️ Kinoni tahrirlash", callback_data="edit_movie")]
    ]
    return InlineKeyboardMarkup(keyboard)