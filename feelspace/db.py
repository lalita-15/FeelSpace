
import os
import psycopg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_db_connection():

    db_password = os.getenv("DB_PASSWORD")

    if not db_password:
        raise ValueError("DB_PASSWORD is not configured in .env file")

    conn = psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "feelspace_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=db_password
    )

    return conn


if __name__ == "__main__":

    try:
        conn = get_db_connection()

        print("PostgreSQL connected successfully!")

        conn.close()

    except Exception as e:
        print("Database connection failed:", e)
