
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# Load .env from the project root (parent directory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def get_db_connection():

    db_password = os.getenv("DB_PASSWORD")

    if not db_password:
        raise ValueError("DB_PASSWORD is not configured in .env file")

    db_host = os.getenv("DB_HOST", "localhost")

    # Local PostgreSQL does not require SSL.
    # Remote/AWS PostgreSQL connections require SSL.
    ssl_mode = "disable" if db_host in ("localhost", "127.0.0.1") else "require"

    conn = psycopg.connect(
        host=db_host,
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "feelspace_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=db_password,
        sslmode=ssl_mode
    )

    return conn


if __name__ == "__main__":

    try:
        conn = get_db_connection()
        print("PostgreSQL connected successfully!")
        conn.close()

    except Exception as e:
        print("Database connection failed:", e)
