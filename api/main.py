import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import psycopg2
from database import get_db_connection
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# --- Configuration ---
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"
EMBEDDING_DIMENSIONS = 1536
TOP_K_CHUNKS = 5

# Create FastAPI app
app = FastAPI(title="RAG Chatbot API")

# Enable CORS for browser clients (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple routes to avoid 404s when testing in a browser
@app.get("/")
async def root():
    return {"message": "RAG Chatbot API is running. Use POST /api/chat with JSON {\"query\": \"...\"}."}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/api/chat")
async def chat_get_note():
    return {"message": "Use POST /api/chat with body {\"query\": \"your question\"}."}

# Pydantic model for the user's query
class Query(BaseModel):
    query: str

# Helper function to generate embedding for a query
def get_query_embedding(text: str) -> list[float]:
    try:
        text = text.replace("\n", " ")
        response = client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL,
            dimensions=EMBEDDING_DIMENSIONS
        )
        return response.data[0].embedding
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating query embedding: {e}")

# Helper function to perform vector search in the database
def semantic_search(query_vector: list[float], top_k: int = TOP_K_CHUNKS) -> list[str]:
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Could not connect to database")
    try:
        cur = conn.cursor()
        # The `<->` operator calculates the L2 distance (Euclidean distance)
        # The `ORDER BY embedding <-> %s` clause performs the vector search
        # This is a very efficient operation with the pgvector index 
        cur.execute(
            "SELECT content FROM document_chunks ORDER BY embedding <-> %s LIMIT %s;",
            (str(query_vector), top_k)
        )
        results = cur.fetchall()
        return [row[0] for row in results]
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    finally:
        cur.close()
        conn.close()

# Helper function to generate the final response using the LLM
def generate_response(query: str, context: list[str]) -> str:
    combined_context = "\n\n".join(context)
    prompt = f"""
    You are an AI assistant specialized in providing information based on the provided context.
    
    If the user's query cannot be answered from the context, respond with "I am sorry, but the information to answer your question is not in my knowledge base." Do not make up an answer.
    
    Context:
    {combined_context}
    
    User Query: {query}
    
    Response:
    """
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {e}")

@app.post("/api/chat")
async def chat_endpoint(query_data: Query):
    # 1. Generate embedding for the user's query
    query_vector = get_query_embedding(query_data.query)
    
    # 2. Perform a semantic search to retrieve relevant context
    retrieved_context = semantic_search(query_vector)
    
    if not retrieved_context:
        return {"response": "I am sorry, but I couldn't find any relevant information in my knowledge base."}
        
    # 3. Generate the final response using the retrieved context
    final_response = generate_response(query_data.query, retrieved_context)
    
    return {"response": final_response}