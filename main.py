from telethon import TelegramClient, events

# 1. Insert your credentials here
API_ID: int
API_HASH = your_api_hash_here'

# 2. Configuration
CHANNEL_USERNAME = 'freelance_ethio' 
TARGET_KEYWORDS = ['python', 'django', 'backend', 'software'] # Add your specific fields
DESTINATION = 'me' 

# Initialize the client
client = TelegramClient('afriwork_session', API_ID, API_HASH)

@client.on(events.NewMessage(chats=CHANNEL_USERNAME))
async def handle_new_job(event):
    # Extract the text of the new message
    message_text = event.message.message or ""
    
    # Check if any of our target keywords are in the job description (case-insensitive)
    if any(keyword.lower() in message_text.lower() for keyword in TARGET_KEYWORDS):
        print(f"Match found! Forwarding job posting...")
        
        # Forward the actual job post to your Saved Messages
        await client.forward_messages(DESTINATION, event.message)
        
        # Send a custom alert message right after it
        await client.send_message(DESTINATION, "🚀 ^ Found a matching job on Afriwork!")

if __name__ == '__main__':
    print(f"Listening for {TARGET_KEYWORDS} on @{CHANNEL_USERNAME} in real-time...")
    # Start the client
    client.start()
    # Keep the script running
    client.run_until_disconnected()
