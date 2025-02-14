import asyncio
import logging
import nest_asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telethon import TelegramClient
from telethon.sessions import StringSession

# تطبيق nest_asyncio لتجنب مشكلة تعشيش حلقات الأحداث
nest_asyncio.apply()

# إعداد سجل الأحداث (logging)
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# ========================
# بيانات إعداد Telethon والبوت
# ========================
api_id = 13183535  # استبدل هذا برقم api_id الخاص بك
api_hash = '1d727fdac5f34ec760e115ac15c47a29'  # استبدل هذا بـ api_hash الخاص بك
bot_token = '7921171909:AAGCygoM0p2Q7QAWLuNgye4hnHzk83bSXz8'  # توكن البوت الخاص بك
channel_username = 'MoviesHM9'  # اسم المستخدم للقناة (بدون @)
SESSION_FILE = "session.txt"

def load_session_string() -> str:
    """يحاول تحميل الجلسة من الملف إن وجدت."""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return f.read().strip()
    return None

def save_session_string(session_str: str):
    """يحفظ الجلسة في الملف."""
    with open(SESSION_FILE, "w") as f:
        f.write(session_str)

session_str = load_session_string()

telethon_client = TelegramClient(
    StringSession(session_str) if session_str else StringSession(),
    api_id, api_hash,
    system_version="4.16.30-vx",
    device_model="BotClient",
    app_version="1.0",
)

async def start_telethon():
    while True:
        try:
            await telethon_client.start()
            save_session_string(telethon_client.session.save())
            logging.info("✅ Telethon client started successfully.")
            break
        except Exception as e:
            logging.error(f"❌ Failed to start Telethon: {e}, retrying in 10 seconds...")
            await asyncio.sleep(10)

async def check_connection():
    while True:
        try:
            await telethon_client.get_me()
            logging.info("✅ Telethon client is active.")
        except Exception as e:
            logging.error(f"❌ Telethon client disconnected: {e}. Restarting...")
            await start_telethon()
        await asyncio.sleep(600)

async def search_movies(query: str, limit=10):
    try:
        messages = await telethon_client.get_messages(channel_username, search=query, limit=limit)
        return messages if messages else []
    except Exception as e:
        logging.error(f"❌ Error in search_movies: {e}")
        return []

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """
    اهلين والله بالاكابر ♥️♥️
انا شغلتي جيبلك افلام ، اعطيني اسم الفيلم ورح دورلك عليه.
غير هيك فيك تشرفنا بكروبنا المتواضع:
    [https://t.me/Movies_group4](https://t.me/Movies_group4)
    -----------------------------------------------------
    طريقة استخدام البوت:
    نكتب 
    /movie اسم الفيلم 
    مثال:
    /movie Hitch
    اذا كان الفيلم مو موجود اتواصل معنا عالكروب
    """
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

async def movie_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال اسم الفيلم بعد الأمر.")
        return

    movie_name = " ".join(context.args)
    await update.message.reply_text(f"🔎 البحث عن: *{movie_name}*...", parse_mode="Markdown")

    try:
        movie_messages = await search_movies(movie_name)
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ أثناء البحث: `{e}`", parse_mode="Markdown")
        return

    if movie_messages:
        user_id = update.message.from_user.id
        tasks = [
            context.bot.copy_message(
                chat_id=user_id, from_chat_id=msg.chat_id, message_id=msg.id
            )
            for msg in reversed(movie_messages)
        ]
        await asyncio.gather(*tasks)
        await update.message.reply_text("✅ جميع النتائج أُرسلت لك!", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ لم يتم العثور على نتائج.")

async def main():
    await start_telethon()
    asyncio.create_task(check_connection())
    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("movie", movie_command))
    logging.info("🚀 Bot is running...")
    await app.run_polling(close_loop=False)

if __name__ == '__main__':
    asyncio.run(main())
