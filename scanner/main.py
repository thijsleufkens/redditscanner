import schedule
import time
import logging
import argparse
import sys
import os
from datetime import datetime, timezone
from database import init_db, insert_posts, get_stats
from fetcher import fetch_all

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Heartbeat-bestand voor het Strongbad-dashboard: de mtime = laatste geslaagde
# fetch-cyclus (Reddit bereikt). Leeg laten/ontbreken -> dashboard toont 'stale'.
HEARTBEAT_FILE = os.environ.get("HEARTBEAT_FILE", "/app/heartbeats/reddit-scout")

def write_heartbeat():
    try:
        os.makedirs(os.path.dirname(HEARTBEAT_FILE), exist_ok=True)
        with open(HEARTBEAT_FILE, "w") as fh:
            fh.write(datetime.now(timezone.utc).isoformat())
    except Exception as e:
        logging.warning(f"Kon heartbeat niet schrijven: {e}")

def job():
    logging.info("Starting fetch cycle...")
    posts = fetch_all()
    if posts:
        count = insert_posts(posts)
        logging.info(f"Inserted {count} new posts into the database.")
        write_heartbeat()
    else:
        logging.warning("No posts fetched in this cycle.")
    logging.info("Fetch cycle complete. Next cycle in 4 hours.")

def print_stats():
    stats = get_stats()
    if not stats:
        print("No data in the database.")
        return
        
    print(f"{'Subreddit':<20} | {'Posts':<10} | {'Last Fetch'}")
    print("-" * 55)
    for row in stats:
        print(f"{row['subreddit']:<20} | {row['count']:<10} | {row['last_fetch']}")

def main():
    parser = argparse.ArgumentParser(description="Reddit RSS Scraper for Manufacturing")
    parser.add_argument("--stats", action="store_true", help="Print database statistics and exit")
    parser.add_argument("--now", action="store_true", help="Run the scraper once and exit")
    args = parser.parse_args()

    # Initialize DB (creates table + WAL mode)
    init_db()

    if args.stats:
        print_stats()
        return

    if args.now:
        job()
        return

    # Initial job run
    job()

    # Schedule the job to run every 4 hours
    schedule.every(4).hours.do(job)

    logging.info("Scraper is running. Scheduled to fetch every 4 hours.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
