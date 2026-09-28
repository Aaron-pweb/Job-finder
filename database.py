import os
import psycopg2
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set.")
    return psycopg2.connect(db_url)

def init_db():
    """Create the processed_jobs table if it doesn't exist."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS processed_jobs (
                        id SERIAL PRIMARY KEY,
                        message_id VARCHAR(255) UNIQUE NOT NULL,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            conn.commit()
            logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def is_job_processed(message_id: str) -> bool:
    """Check if a message_id has already been processed."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM processed_jobs WHERE message_id = %s", 
                    (message_id,)
                )
                return cur.fetchone() is not None
    except Exception as e:
        logger.error(f"Error checking if job is processed: {e}")
        return False

def mark_job_processed(message_id: str):
    """Insert the message_id into the processed_jobs table."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO processed_jobs (message_id) VALUES (%s) ON CONFLICT (message_id) DO NOTHING",
                    (message_id,)
                )
            conn.commit()
    except Exception as e:
        logger.error(f"Error marking job as processed: {e}")
