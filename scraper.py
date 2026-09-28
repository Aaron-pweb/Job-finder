import os
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def get_target_categories():
    categories_str = os.environ.get("TARGET_CATEGORIES", "")
    return [c.strip().lower() for c in categories_str.split(",") if c.strip()]

def matches_criteria(text: str, categories: list) -> bool:
    """Basic keyword matching (case-insensitive)."""
    if not categories:
        return True # If no categories specified, match everything
    
    text_lower = text.lower()
    for cat in categories:
        if cat in text_lower:
            return True
    return False

def scrape_jobs():
    """Scrapes the Telegram channel and yields matching jobs."""
    url = os.environ.get("TELEGRAM_CHANNEL_URL")
    if not url:
        logger.error("TELEGRAM_CHANNEL_URL is missing.")
        return []

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message')
        
        target_categories = get_target_categories()
        matching_jobs = []
        
        for msg in messages:
            # Extract message ID (e.g., examplechannel/123)
            msg_link = msg.get('data-post')
            if not msg_link:
                continue
                
            msg_id = msg_link.split('/')[-1] if '/' in msg_link else msg_link
            
            # Extract text
            text_div = msg.find('div', class_='tgme_widget_message_text')
            if not text_div:
                continue
                
            text_content = text_div.get_text(separator='\n').strip()
            
            if matches_criteria(text_content, target_categories):
                # Construct the direct link to the post
                channel_name = url.strip('/').split('/')[-1]
                if '?' in channel_name:
                    channel_name = channel_name.split('?')[0]
                post_url = f"https://t.me/{channel_name}/{msg_id}"
                
                job_data = {
                    "id": msg_id,
                    "text": text_content,
                    "url": post_url
                }
                matching_jobs.append(job_data)
                
        return matching_jobs

    except Exception as e:
        logger.error(f"Error scraping Telegram channel: {e}")
        return []
