import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "data/reddit_posts.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Enable WAL mode for better concurrent access
    cursor.execute("PRAGMA journal_mode=WAL")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            subreddit TEXT,
            title TEXT,
            selftext TEXT,
            author TEXT,
            url TEXT,
            score INTEGER,
            num_comments INTEGER,
            created_utc DATETIME,
            fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_processed INTEGER DEFAULT 0
        )
    """)
    
    # Index for fast queries by the scheduled task
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_unprocessed_created 
        ON posts (is_processed, created_utc)
    """)
    
    conn.commit()
    conn.close()

def insert_posts(posts):
    conn = get_connection()
    cursor = conn.cursor()
    
    for post in posts:
        cursor.execute("""
            INSERT OR IGNORE INTO posts (
                id, subreddit, title, selftext, author, url, score, num_comments, created_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post['id'], post['subreddit'], post['title'], post['selftext'],
            post['author'], post['url'], post['score'], post['num_comments'],
            post['created_utc']
        ))
    
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT subreddit, COUNT(*) as count, MAX(fetched_at) as last_fetch
        FROM posts
        GROUP BY subreddit
    """)
    
    stats = cursor.fetchall()
    conn.close()
    return stats
