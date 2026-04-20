import feedparser
import time
import logging
from datetime import datetime

SUBREDDITS = [
    "manufacturing",
    "ERP",
    "PowerBI",
    "smallbusiness",
    "analytics",
    "supplychain",
    "leanmanufacturing"
]

USER_AGENT = "Reddit-RSS-Scraper/1.0 (for LinkedIn Content Ideas; contact: thijs@example.com)"

def fetch_subreddit_rss(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/.rss"
    logging.info(f"Fetching feed for r/{subreddit}...")
    
    # Reddit RSS returns XML, feedparser handles it
    feed = feedparser.parse(url, agent=USER_AGENT)
    
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
