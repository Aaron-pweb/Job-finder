import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import re

# Configuration
URL = 'https://t.me/s/freelance_ethio'
TARGET_KEYWORDS = ['software', 'developer', 'python', 'react', 'backend', 'frontend']

def scrape_recent_jobs():
    print(f"Scraping {URL} for jobs posted in the last hour...")
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        html = urllib.request.urlopen(req).read()
    except Exception as e:
        print(f"Failed to fetch page: {e}")
        return

    soup = BeautifulSoup(html, 'html.parser')
    messages = soup.find_all('div', class_='tgme_widget_message_wrap')
    
    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)
    
    jobs_found = 0
    matched_jobs = []

    for msg in messages:
        time_tag = msg.find('time')
        if not time_tag or not time_tag.has_attr('datetime'):
            continue
            
        # Parse Telegram's datetime (e.g., 2026-08-28T09:41:09+00:00)
        msg_time_str = time_tag['datetime'].replace('Z', '+00:00')
        msg_time = datetime.fromisoformat(msg_time_str)
        
        # Check if posted in the last hour
        if msg_time >= one_hour_ago:
            jobs_found += 1
            
            # Extract text
            text_div = msg.find('div', class_='tgme_widget_message_text')
            if not text_div:
                continue
                
            full_text = text_div.get_text(separator='\n', strip=True)
            
            # Extract Job Title for display
            title_match = re.search(r'Job Title:\s*(.+?)\n', full_text)
            job_title = title_match.group(1) if title_match else "Unknown Title"
            
            # Check for keywords
            matched_keywords = [
                kw for kw in TARGET_KEYWORDS 
                if re.search(rf'\b{re.escape(kw)}\b', full_text, re.IGNORECASE)
            ]
            
            if matched_keywords:
                matched_jobs.append({
                    'title': job_title,
                    'time': msg_time.strftime("%H:%M UTC"),
                    'keywords': matched_keywords,
                    'link': f"https://t.me/freelance_ethio/{msg.find('div', class_='tgme_widget_message')['data-post'].split('/')[-1]}"
                })

    print(f"\nTotal jobs posted in the last hour: {jobs_found}")
    print(f"Jobs matching your keywords ({', '.join(TARGET_KEYWORDS)}): {len(matched_jobs)}\n")
    
    for job in matched_jobs:
        print(f"🎯 MATCH: {job['title']}")
        print(f"   Keywords: {', '.join(job['keywords'])}")
        print(f"   Posted at: {job['time']}")
        print(f"   Link: {job['link']}\n")

if __name__ == '__main__':
    scrape_recent_jobs()
