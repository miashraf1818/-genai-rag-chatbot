# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("your api key")
PINECONE_API_KEY = os.getenv("your api key ")
PINECONE_ENV = os.getenv("us-east-1")

# Pinecone settings
INDEX_NAME = "my-genai-index"

# Model settings
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"  # 1024 dims (what you're downloading)
GROQ_MODEL = "llama3-8b-8192"  # Llama 3 via Groq
