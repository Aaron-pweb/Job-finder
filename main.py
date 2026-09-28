import time
import os
import logging
from api.cron import run_job_scraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    interval_minutes = int(os.environ.get("SCRAPE_INTERVAL_MINUTES", "10"))
    interval_seconds = interval_minutes * 60
    
    logging.info(f"Starting continuous scraper every {interval_minutes} minutes...")
    
    # Run immediately once
    try:
        run_job_scraper()
    except Exception as e:
        logging.error(f"Error in scraping loop: {e}")
        
    while True:
        logging.info(f"Sleeping for {interval_minutes} minutes...")
        time.sleep(interval_seconds)
        
        try:
            run_job_scraper()
        except Exception as e:
            logging.error(f"Error in scraping loop: {e}")
