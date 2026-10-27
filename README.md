# Reddit RSS scanner

A small Docker container that reads the RSS feeds of a handful of subreddits every
four hours and stores the posts in a SQLite database. Nothing more: no Reddit
account, no API key, no scoring. The scoring happens elsewhere, on top of the
database (see [How I used it](#how-i-used-it)).

I built it for an experiment: can a language model pull out what people in
organisations struggle with, so I'd have material for my own LinkedIn posts? The
short answer was no, but the scanner itself works fine and is easy to reuse.

## Getting started

You need [Docker](https://docs.docker.com/get-docker/) with Compose.

```bash
git clone https://github.com/thijsleufkens/redditscanner.git
cd redditscanner
docker compose up -d
```

The container fetches once at start-up and then every four hours. The database
ends up in `./data/reddit_posts.db`.

```bash
# How many posts per subreddit, and when was the last fetch?
docker exec reddit-scanner python main.py --stats

# Fetch right now instead of waiting
docker exec reddit-scanner python main.py --now
```

## Configuration

All settings are environment variables in `docker-compose.yml`:

| Variable | Default | What it does |
|---|---|---|
| `SUBREDDITS` | manufacturing, ERP, PowerBI, smallbusiness, analytics, supplychain, leanmanufacturing | Comma-separated list of subreddits |
| `USER_AGENT` | a generic one | Reddit asks for a descriptive User-Agent with a way to contact you. Set your own. |
| `DB_PATH` | `/app/data/reddit_posts.db` | Where the database lives inside the container |
| `HEARTBEAT_FILE` | (off) | If set, this file is rewritten after every successful fetch, so a monitoring tool can notice when the scanner stops |

## The database

One table, `posts`:

| Column | Notes |
|---|---|
| `id` | Reddit post id (primary key, so a post is stored only once) |
| `subreddit`, `title`, `selftext`, `author`, `url` | From the feed; `selftext` is HTML |
| `created_utc` | The feed's `updated` timestamp |
| `fetched_at` | When the scanner first saw the post |
| `score`, `num_comments` | Always 0: the RSS feed doesn't include them |
| `is_processed` | Free flag for whatever reads the database (0 by default) |

The database runs in WAL mode, so other programs can read it while the scanner
is writing. Open it read-only (`file:reddit_posts.db?mode=ro`) if you want to be
safe.

## How I used it

The scanner ran from March to October 2026 and collected about 10,000 posts. I
tried two ways of finding the useful ones:

1. **A weekly scan with Claude** (March to May). Every week Claude read the new
   posts and gave each one two scores from 1 to 5: is this about two systems or
   departments that don't connect, and is there a real story in it? Only posts
   scoring at least 3 on both made it into a weekly report, with a quote, a
   one-line summary and a possible angle. The prompt is in
   [`examples/weekly-scan-prompt.md`](examples/weekly-scan-prompt.md) (in Dutch).
2. **A daily local filter** (June and July). A small embedding model
   (`nomic-embed-text` via Ollama) compared each new post with five short theme
   descriptions from my work and kept the posts that were similar enough. A
   local LLM wrote a possible angle for each, and I got at most six a day as
   cards to approve or reject. The themes and the selection rules are in
   [`examples/themes.md`](examples/themes.md).

**What came out of it:** the scans showed clearly what people run into, but
hardly anything I could use for a post. The stories weren't about things I had
experienced myself, so they rarely reached the quality I want. After three days I
stopped rating the cards. The scanner still runs as a searchable archive.

## Things to know

- Reddit's RSS feed only returns the latest ±25 posts per subreddit. For a busy
  subreddit, four hours can be too long and you'll miss posts. Fetch more often
  if that matters to you.
- Reddit rate-limits anonymous feed requests fairly aggressively and then
  answers with HTTP 429 and an empty feed. The scanner logs that as a warning;
  if you see it often, set a clear `USER_AGENT` and fetch less often.
- You're storing other people's posts, including their usernames. Fine for
  personal research; check [Reddit's terms](https://redditinc.com/policies) before
  you do more with it.

## License

[0BSD](LICENSE): do whatever you want with it, no attribution needed.
