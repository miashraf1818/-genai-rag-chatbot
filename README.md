# GenAI RAG Chatbot

Production-ready RAG chatbot with FastAPI, React, and AWS.

## Features
- Real-time AI chat with streaming
- RAG pipeline (Pinecone + Llama 3.3)
- User authentication
- Admin panel
- AWS deployment

## Tech Stack
- Backend: FastAPI, Python 3.13
- Frontend: React, TypeScript
- AI: Groq (Llama 3.3), Pinecone
- Database: PostgreSQL
- Cloud: AWS

## Setup

1. Clone repo
2. Copy .env.example to .env
3. Add your API keys
4. Run: `uvicorn backend.main:app --reload`
