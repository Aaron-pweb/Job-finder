import os
import sys
import logging
from http.server import BaseHTTPRequestHandler

# Add parent directory to path so imports work in Vercel
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db, is_job_processed, mark_job_processed
from scraper import scrape_jobs
from notifier import send_telegram_alert

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_job_scraper():
    logger.info("Starting job scraper task...")
    
    # Initialize DB (creates table if not exists)
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return "Database initialization failed", 500

    # Scrape jobs
    jobs = scrape_jobs()
    if not jobs:
        logger.info("No matching jobs found in this run.")
        return "No jobs found", 200
        
    new_jobs_count = 0
    
    for job in jobs:
        if not is_job_processed(job["id"]):
            logger.info(f"Found new matching job: {job['id']}")
            
            # Format the alert message
            preview = job["text"][:200] + "..." if len(job["text"]) > 200 else job["text"]
            message = (
                f"<b>New Job Match Found!</b>\n\n"
                f"<b>Preview:</b>\n<i>{preview}</i>\n\n"
                f"<a href='{job['url']}'>View Post on Telegram</a>"
            )
            
            # Send alert
            success = send_telegram_alert(message)
            
            if success:
                # Mark as processed only if alert was sent successfully
                mark_job_processed(job["id"])
                new_jobs_count += 1
                
    logger.info(f"Finished scraping. {new_jobs_count} new alerts sent.")
    return f"Processed {new_jobs_count} new jobs", 200

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        msg, status = run_job_scraper()
        self.send_response(status)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(msg.encode('utf-8'))
        return
