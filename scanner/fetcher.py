import feedparser
import os
import time
import logging
from datetime import datetime

DEFAULT_SUBREDDITS = [
    "manufacturing",
    "ERP",
    "PowerBI",
    "smallbusiness",
    "analytics",
    "supplychain",
    "leanmanufacturing"
]

# Comma-separated list, e.g. SUBREDDITS="manufacturing,ERP"
SUBREDDITS = [s.strip() for s in os.getenv("SUBREDDITS", ",".join(DEFAULT_SUBREDDITS)).split(",") if s.strip()]

# Reddit asks for a descriptive User-Agent with a way to contact you. Set your own.
USER_AGENT = os.getenv("USER_AGENT", "Reddit-RSS-Scraper/1.0 (personal research; set USER_AGENT to add your contact)")

# How often to retry a subreddit after a rate limit (HTTP 429)
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))

def fetch_subreddit_rss(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/.rss"
    logging.info(f"Fetching feed for r/{subreddit}...")
    
    # Reddit RSS returns XML, feedparser handles it
    feed = feedparser.parse(url, agent=USER_AGENT)

    # Reddit answers a rate limit with HTTP 429 and an empty feed, which
    # feedparser doesn't flag as an error. Check the status ourselves.
    # Anonymous requests can be limited to one per minute per IP address, so
    # wait until the window resets (x-ratelimit-reset, in seconds) and retry.
    for _ in range(MAX_RETRIES):
        if feed.get('status') != 429:
            break
        try:
            wait = float(feed.get('headers', {}).get('x-ratelimit-reset', 60))
        except ValueError:
            wait = 60
        wait = min(wait, 120) + 2
        logging.info(f"r/{subreddit}: rate limited, retrying in {wait:.0f}s")
        time.sleep(wait)
        feed = feedparser.parse(url, agent=USER_AGENT)

    status = feed.get('status')
    if status is not None and status != 200:
        logging.warning(f"r/{subreddit}: HTTP {status}, no posts fetched")
        return []

    if feed.bozo:
        logging.error(f"Error parsing feed for {subreddit}: {feed.bozo_exception}")
        return []
        
    posts = []
    for entry in feed.entries:
        # entry.id is usually something like 't3_123456' or the full URL
        # We'll use the entry.id as the primary key
        
        # Extract metadata from the entry
        # Note: feedparser might not always capture all reddit-specific fields easily
        # but common RSS fields map well.
        
        # Reddit RSS structure:
        # title, link, author, updated (ISO 8601), content (HTML)
        
        post_id = entry.get('id', entry.link)
        
        posts.append({
            'id': post_id,
            'subreddit': subreddit,
            'title': entry.get('title', ''),
            'selftext': entry.get('summary', entry.get('description', '')),
            'author': entry.get('author', 'anonymous'),
            'url': entry.get('link', ''),
            'score': 0, # Not readily available in RSS without extra parsing
            'num_comments': 0, # Not readily available in RSS
            'created_utc': entry.get('updated', datetime.now().isoformat())
        })
    
    return posts

def fetch_all():
    all_posts = []
    for sub in SUBREDDITS:
        try:
            posts = fetch_subreddit_rss(sub)
            all_posts.extend(posts)
            # Respect rate limits: max 1 request per 2 seconds
            time.sleep(2)
        except Exception as e:
            logging.error(f"Failed to fetch r/{sub}: {e}")
            
    return all_posts
