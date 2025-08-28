import os
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI
import psycopg2
from psycopg2.extras import Json
from unstructured.partition.auto import partition
from unstructured.chunking.title import chunk_by_title
from api.database import get_db_connection

# Load environment variables
load_dotenv(override=True)

# Initialize OpenAI client
client = OpenAI()

# --- Configuration ---
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
MAX_TOKENS_PER_CHUNK = 100

# --- Helper Functions ---

def count_tokens(text: str) -> int:
    """Counts tokens using OpenAI's tiktoken encoder."""
    enc = tiktoken.encoding_for_model(EMBEDDING_MODEL)
    return len(enc.encode(text))

def get_embedding(text: str) -> list[float]:
    """Generates an embedding for the given text using OpenAI's API."""
    try:
        text = text.replace("\n", " ")
        response = client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL,
            dimensions=EMBEDDING_DIMENSIONS
        )
        print(f"Attempting to generate embedding for text: '{text[:100]}...'")
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding for text: {text[:50]}... Error: {e}")
        return []

def process_document(file_path: str):
    """
    Loads a document, chunks it, generates embeddings, and stores in the DB.
    """
    print(f"Processing document: {file_path}")
    try:
        elements = partition(file_path)
        # Use chunk_by_title with the elements directly
        chunks = chunk_by_title(
            elements,
            max_characters=MAX_TOKENS_PER_CHUNK * 4,
            new_after_n_chars=MAX_TOKENS_PER_CHUNK * 4
        )

        data_to_insert = []
        for i, chunk in enumerate(chunks):
            chunk_text = str(chunk)
            if not chunk_text.strip():
                continue

            embedding = get_embedding(chunk_text)
            if embedding:
                print(f"Successfully generated embedding for chunk {i+1}.")
                data_to_insert.append((
                    chunk_text,
                    embedding,
                    os.path.basename(file_path),
                    Json({"chunk_number": i + 1})
                ))
        print(f"Data to be inserted: {len(data_to_insert)} items")
        if data_to_insert:
            insert_chunks_into_db(data_to_insert)
            print(f"Successfully stored {len(data_to_insert)} chunks from {file_path}")
        else:
            print(f"No valid chunks found or embeddings generated for {file_path}.")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def insert_chunks_into_db(data: list):
    """Inserts a list of (content, embedding, source, metadata) tuples into the database."""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.executemany(
                "INSERT INTO document_chunks (content, embedding, source, metadata) VALUES (%s, %s, %s, %s)",
                data
            )
            conn.commit()
            print("Chunks inserted successfully.")
        except Exception as e:
            print(f"Error inserting chunks into database: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    else:
        print("Failed to get DB connection for insertion.")

if __name__ == "__main__":
    # Ensure a 'documents' directory exists
    os.makedirs("documents", exist_ok=True)
    
    # Sample text file to ingest
    sample_content = """
# Section 1: Introduction to AI and RAG
Artificial Intelligence (AI) is a rapidly evolving field. Large Language Models (LLMs) are a key component of modern AI systems, capable of understanding and generating human-like text. Retrieval-Augmented Generation (RAG) enhances LLMs by providing them with external, up-to-date knowledge. This project aims to build a RAG chatbot. Vector databases like pgvector are essential for RAG, as they allow for fast and efficient similarity search on text embeddings.

# Section 2: The RAG Workflow
The process of building a RAG system involves several steps. First, documents are ingested and split into smaller chunks. Next, these chunks are converted into numerical representations called vector embeddings. Finally, these embeddings are stored in a vector database. When a user asks a question, the system retrieves the most relevant chunks and uses them as context for the LLM to generate an accurate response.
"""
    
    with open("documents/ai_concepts.txt", "w") as f:
        f.write(sample_content)

    # Make sure you have your OPENAI_API_KEY in your .env file
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY is not set in your .env file. Please add it before running.")
    else:
        for filename in os.listdir("documents"):
            file_path = os.path.join("documents", filename)
            if os.path.isfile(file_path):
                process_document(file_path)

        # Verify the chunks in the database
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM document_chunks;")
            count = cur.fetchone()[0]
            print(f"\nTotal chunks in database: {count}")
            cur.close()
            conn.close()