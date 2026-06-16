import aiosqlite
import os

DB_NAME = "movies.db"

async def init_db():
    """Bazani ishga tushirish va jadvallarni yaratish."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                code TEXT PRIMARY KEY,
                title TEXT,
                file_id TEXT
            )
        """)
        await db.commit()

async def add_movie(code, title, file_id):
    """Yangi kino qo'shish yoki mavjudini yangilash."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR REPLACE INTO movies (code, title, file_id) VALUES (?, ?, ?)",
            (code.upper(), title, file_id)
        )
        await db.commit()

async def get_movie(code):
    """Kino kod orqali qidirish."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM movies WHERE code = ?", (code.upper(),)) as cursor:
            return await cursor.fetchone()

async def get_all_movies():
    """Barcha kinolar ro'yxatini olish."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT code, title FROM movies") as cursor:
            return await cursor.fetchall()

async def delete_movie(code):
    """Kinoni o'chirish."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM movies WHERE code = ?", (code.upper(),))
        await db.commit()

async def update_movie_name(code, new_name):
    """Kino nomini tahrirlash."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE movies SET title = ? WHERE code = ?", (new_name, code.upper()))
        await db.commit()