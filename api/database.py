import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def initialize_database():
    """Connects to the database and creates the chunks table."""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()

            # Enable the pgvector extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Create the document_chunks table
            # vector(1536) for OpenAI's text-embedding-3-small
            cur.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding vector(1536) NOT NULL,
                    source TEXT,
                    metadata JSONB
                );
            """)
            conn.commit()
            print("pgvector extension enabled.")
            print("Table 'document_chunks' ensured.")
            print("Database initialized successfully.")

        except Exception as e:
            print(f"Error initializing database: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    else:
        print("Could not establish database connection.")

if __name__ == "__main__":
    initialize_database()