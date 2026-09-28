import os
import requests
import logging

logger = logging.getLogger(__name__)

def send_telegram_alert(message_text: str):
    """Sends a message via the Telegram Bot API."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        logger.error("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is missing. Cannot send alert.")
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Successfully sent Telegram alert.")
        return True
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")
        return False
