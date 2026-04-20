# Reddit RSS Scraper for Manufacturing

This is a simple Docker-based scraper that fetches Reddit RSS feeds from manufacturing-related subreddits and stores them in a SQLite database.

## Architecture
- **Scraper**: A Python script running in a Docker container.
- **Database**: SQLite database stored in a persistent volume (host-mounted).
- **Scheduling**: Fetches feeds every 4 hours using the `schedule` library.
- **Persistence**: Database is in WAL mode, allowing external reads while the scraper is running.

## Subreddits Tracked
- /r/manufacturing
- /r/ERP
- /r/PowerBI
- /r/smallbusiness
- /r/analytics
- /r/supplychain
- /r/leanmanufacturing

## Getting Started

### 1. Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 2. Setup
Clone the repository and run:
```bash
docker compose up -d
```

By default, the database is stored at `~/Documents/reddit-scanner/data/reddit_posts.db`.

### 3. CLI Statistics
To view statistics of the database:
```bash
docker exec reddit-manufacturing-scanner python main.py --stats
```

To run a fetch cycle immediately:
```bash
docker exec reddit-manufacturing-scanner python main.py --now
```

## SQLite Schema
The `posts` table includes:
- `id`: Reddit post ID (Primary Key)
- `subreddit`: Name of the subreddit
- `title`: Post title
- `selftext`: Content of the post
- `author`: Post author
- `url`: Link to the post
- `score`: Placeholder (not available in RSS)
- `num_comments`: Placeholder (not available in RSS)
- `created_utc`: Post creation time
- `fetched_at`: Time the post was fetched
- `is_processed`: Flag for external scheduled tasks (defaults to 0)

An index is created on `(is_processed, created_utc)` for efficient querying.

## License
MIT
