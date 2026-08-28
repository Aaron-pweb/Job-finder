import os
import re
import requests
import asyncpg
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables from .env file (useful for local testing)
load_dotenv()

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")  # Neon Postgres connection string

if TELEGRAM_BOT_TOKEN:
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
else:
    bot = None
    application = None

# --- DATABASE HELPER FUNCTIONS ---
async def init_db():
    """Creates the users table if it doesn't exist."""
    if not DATABASE_URL:
        return
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            chat_id BIGINT PRIMARY KEY,
            preference TEXT NOT NULL
        )
    ''')
    await conn.close()

async def save_user_preference(chat_id: int, preference: str):
    conn = await asyncpg.connect(DATABASE_URL)
    # UPSERT: Insert or update if exists
    await conn.execute('''
        INSERT INTO user_preferences (chat_id, preference) 
        VALUES ($1, $2)
        ON CONFLICT (chat_id) DO UPDATE SET preference = $2
    ''', chat_id, preference)
    await conn.close()

async def get_all_users():
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch('SELECT chat_id, preference FROM user_preferences')
    await conn.close()
    return rows

# Initialize DB when FastAPI starts
@app.on_event("startup")
async def startup_event():
    try:
        await init_db()
    except Exception as e:
        print(f"Database initialization failed: {e}")

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I am your Job Finder Bot. 🕵️‍♂️\n\n"
        "What kind of job are you looking for? (e.g., 'software', 'marketing', 'teaching')\n"
        "Just type your preferred field below!"
    )

async def handle_user_preference(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_input = update.message.text.strip().lower()
    
    if not DATABASE_URL:
        await update.message.reply_text("Database is not configured yet!")
        return

    try:
        await save_user_preference(chat_id, user_input)
        await update.message.reply_text(
            f"✅ Got it! I have saved your preference as: '{user_input}'.\n\n"
            "I will check the Afriwork channel every hour and notify you if I find a match."
        )
    except Exception as e:
        print(f"Error saving preference: {e}")
        await update.message.reply_text("Sorry, there was an error saving your preference.")

if application:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_preference))

# --- WEBHOOK ENDPOINT ---
@app.post("/api/webhook")
async def webhook(request: Request):
    if not application:
        return {"error": "Bot token not configured"}
        
    data = await request.json()
    update = Update.de_json(data, bot)
    
    await application.initialize()
    await application.process_update(update)
    
    return {"status": "ok"}

# --- CRON JOB ENDPOINT ---
@app.get("/api/cron")
async def cron_job():
    if not bot or not DATABASE_URL:
        return {"error": "Bot token or Database URL not configured"}

    url = 'https://t.me/s/freelance_ethio'
    try:
        html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
    except Exception as e:
        return {"error": f"Failed to fetch page: {str(e)}"}

    soup = BeautifulSoup(html, 'html.parser')
    messages = soup.find_all('div', class_='tgme_widget_message_wrap')
    
    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)
    
    recent_jobs = []

    for msg in messages:
        time_tag = msg.find('time')
        if not time_tag or not time_tag.has_attr('datetime'):
            continue
            
        msg_time = datetime.fromisoformat(time_tag['datetime'].replace('Z', '+00:00'))
        
        if msg_time >= one_hour_ago:
            text_div = msg.find('div', class_='tgme_widget_message_text')
            if not text_div:
                continue
                
            full_text = text_div.get_text(separator='\n', strip=True)
            title_match = re.search(r'Job Title:\s*(.+?)\n', full_text)
            job_title = title_match.group(1) if title_match else "Unknown Title"
            job_link = f"https://t.me/freelance_ethio/{msg.find('div', class_='tgme_widget_message')['data-post'].split('/')[-1]}"
            
            recent_jobs.append({
                'title': job_title,
                'full_text': full_text.lower(),
                'link': job_link
            })

    # Fetch users from database
    try:
        users = await get_all_users()
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

    matches_sent = 0
    for row in users:
        chat_id = row['chat_id']
        preference = row['preference']
        
        for job in recent_jobs:
            if re.search(rf'\b{re.escape(preference)}\b', job['full_text']):
                try:
                    await bot.send_message(
                        chat_id=chat_id, 
                        text=f"🚀 New Match Found for '{preference}'!\n\n"
                             f"🎯 {job['title']}\n"
                             f"🔗 {job['link']}"
                    )
                    matches_sent += 1
                except Exception as e:
                    print(f"Failed to send to {chat_id}: {e}")

    return {"status": "ok", "jobs_checked": len(recent_jobs), "matches_sent": matches_sent}
