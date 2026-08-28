import os
import re
from telethon import TelegramClient, events
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 1. Credentials (Get these from https://my.telegram.org)
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

if not API_ID or not API_HASH:
    raise ValueError("API_ID and API_HASH must be set in the .env file")

# 2. Configuration
# Note: Use the exact channel username (without @). 
# E.g., 'freelance_ethio' or 'afriworket'
CHANNEL_USERNAME = 'freelance_ethio' 

# Target fields/keywords to look for
TARGET_KEYWORDS = [
    'software', 'python', 'django', 'backend', 'frontend', 
    'developer', 'programmer', 'web', 'react', 'node', 'app'
] 

# The destination for matched job postings ('me' forwards to your Saved Messages)
DESTINATION = 'me' 

# Initialize the client
client = TelegramClient('afriwork_session', int(API_ID), API_HASH)

@client.on(events.NewMessage(chats=CHANNEL_USERNAME))
async def handle_new_job(event):
    message_text = event.message.message or ""
    
    # We use regex to ensure we match whole words and ignore case.
    # This prevents matching "app" inside "apple".
    matched_keywords = []
    for keyword in TARGET_KEYWORDS:
        if re.search(rf'\b{re.escape(keyword)}\b', message_text, re.IGNORECASE):
            matched_keywords.append(keyword)
            
    if matched_keywords:
        print(f"Match found for: {', '.join(matched_keywords)}! Forwarding job posting...")
        
        try:
            # Forward the actual job post to your Saved Messages
            await client.forward_messages(DESTINATION, event.message)
            
            # Send a custom alert message right after it
            await client.send_message(
                DESTINATION, 
                f"Found a matching job on Afriwork! Matched keywords: {', '.join(matched_keywords)}"
            )
        except Exception as e:
            print(f"Error forwarding message: {e}")

if __name__ == '__main__':
    print(f"Starting Job Finder Bot...")
    print(f"Listening for keywords: {TARGET_KEYWORDS}")
    print(f"Monitoring channel: @{CHANNEL_USERNAME}")
    
    # Start the client
    client.start()
    
    print("Bot is running. ")
    # Keep the script running
    client.run_until_disconnected()
