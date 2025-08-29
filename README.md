# RAG Chatbot

This project is a simple implementation of a Retrieval-Augmented Generation (RAG) chatbot. It uses a FastAPI backend for the API, a Next.js frontend for the user interface, and a PostgreSQL database with the pgvector extension for storing and retrieving document embeddings.

## Project Overview

The chatbot answers questions based on a set of documents provided to it. The core of the application is the RAG pipeline, which involves the following steps:

1.  **Document Ingestion and Chunking**: Text documents are loaded and split into smaller, manageable chunks.
2.  **Vector Embeddings**: Each chunk is converted into a numerical representation (a vector embedding) using OpenAI's `text-embedding-3-small` model.
3.  **Storage**: These embeddings are stored in a PostgreSQL database with the `pgvector` extension enabled.
4.  **Retrieval**: When a user asks a question, the query is converted into a vector embedding. A semantic search is then performed on the database to find the most relevant document chunks based on the similarity of their embeddings to the query embedding.
5.  **Generation**: The retrieved chunks are provided as context to a Large Language Model (LLM), in this case, OpenAI's `gpt-4o-mini`, which then generates a response to the user's query based on the provided information.

## Technology Stack

### Backend

- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.13+.
- **OpenAI API**: Used for generating text embeddings and for the final response generation by the LLM.
- **psycopg2-binary**: A PostgreSQL adapter for Python.
- **Unstructured**: A library for parsing and chunking various document types.
- **Tiktoken**: A tokenizer by OpenAI used to count tokens in a string.
- **Uvicorn**: An ASGI server for running the FastAPI application.

### Frontend

- **Next.js**: A React framework for building user interfaces.
- **React**: A JavaScript library for building user interfaces.

### Database

- **PostgreSQL**: An open-source object-relational database system.
- **pgvector**: A PostgreSQL extension for vector similarity search.

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- Python 3.13
- Node.js and npm
- An OpenAI API key

### Installation and Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/agajankush/rag_chatbot_app.git
    cd rag-chatbot-app
    ```

2.  **Set up environment variables:**

    Create a `.env` file in the `api` directory and add your OpenAI API key and database credentials:

    ```
    OPENAI_API_KEY="your-openai-api-key"
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=rag_db
    DB_USER=user
    DB_PASSWORD=password
    ```

    _Note: The database credentials should match the ones in `docker-compose.yml`._

3.  **Start the database:**

    ```bash
    docker-compose up -d
    ```

4.  **Install dependencies:**

    - **Backend:**
      ```bash
      uv pip install -r api/requirements.txt
      ```
    - **Frontend:**
      ```bash
      npm install --prefix frontend
      ```

5.  **Initialize the database and ingest data:**

    ```bash
    python -m api.database
    python -m api.ingestion
    ```

    This will set up the necessary tables and process the documents in the `api/documents` directory.

6.  **Run the application:**

    - **Backend:**
      ```bash
      uvicorn api.main:app --reload
      ```
    - **Frontend:**
      ```bash
      npm run dev --prefix frontend
      ```

7.  **Access the application:**
    Open your browser and navigate to `http://localhost:3000`.

## Usage

Once the application is running, you can interact with the chatbot through the web interface. Type a question into the input field and press "Send". The chatbot will then provide an answer based on the information in the documents it has processed.

My apologies for the confusion. The issue is with how I'm generating the response, not the content of the document itself. I will now provide you with a single block of Markdown that you can copy directly. This block contains all the content from the "Vercel Deployment" section of the README, correctly formatted for you.

---

### ☁️ Vercel Deployment

This project is configured for a seamless deployment on Vercel.

### 1. Set up Neon.tech

Your deployed application needs a cloud-hosted database. The easiest way to do this is with [**Neon.tech**](https://neon.tech/).

1. Create an account and a new PostgreSQL project.
2. Copy your connection string credentials (host, user, password, db name, and ssl mode).
3. Use these credentials to manually run `ingestion.py` from your local machine to populate the cloud database.

### 2. Configure Vercel Environment Variables

Log in to your Vercel dashboard and import your Git repository. Before deploying, go to **Settings > Environment Variables** and add your credentials from Neon.tech and OpenAI.

### 3. Deploy

Vercel will automatically detect your project structure and deploy both the Next.js frontend and the FastAPI backend as serverless functions. Your application will be live in minutes!
