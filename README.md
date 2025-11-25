# 🤖 GenAI RAG Chatbot

A production-ready, full-stack AI chatbot that uses Retrieval-Augmented Generation (RAG) to let users securely chat with their private documents (PDF, TXT). Built for real-time streaming, multi-tenant security, and easy deployment with Docker and AWS.

![Project Banner](https://via.placeholder.com/1200x400?text=GenAI+RAG+Chatbot+Dashboard)

One-liner
A production-grade, full-stack AI application that uses RAG to let users chat securely with their own private documents.

✨ Key Features
- RAG pipeline: upload PDF/TXT documents and chat with their content.
- Pinecone vector store for fast, semantic retrieval.
- Llama 3 (via Groq) for generation with streaming support.
- Real-time streaming responses over WebSockets for a ChatGPT-like UX.
- Google OAuth 2.0 for secure sign-in and JWT-based sessions.
- Row-Level Security (RLS) and user isolation: users only access their own documents and chat history.
- Dockerized full-stack for consistent local and cloud deployments.

🧩 Tech Stack

| Component      | Technology                                         |
| :------------- | :------------------------------------------------- |
| Frontend       | Next.js 14 (React 18), TypeScript, Tailwind CSS    |
| Backend        | FastAPI (Python 3.11), WebSockets, Pydantic, SQLAlchemy |
| Vector DB      | Pinecone                                           |
| Model / Inference | Llama 3 (via Groq LPU)                         |
| Database       | PostgreSQL 15                                      |
| Infra          | Docker, Docker Compose, AWS EC2, Nginx             |

🚀 Quick Start (Local)

Prerequisites: Docker & Docker Compose, Git

1. Clone the repo
```bash
git clone https://github.com/miashraf1818/genai-rag-chatbot.git
cd genai-rag-chatbot
```

2. Copy and configure env
```bash
cp .env.example .env
# Edit .env and add API keys (GROQ_API_KEY, PINECONE_API_KEY, GOOGLE_CLIENT_ID, etc.)
```

3. Build and run with Docker
```bash
docker compose up -d --build
```

4. Open the app
- Frontend: http://localhost:3000
- Backend API docs (FastAPI): http://localhost:8000/docs

☁️ Deployment (AWS EC2)

See deployment_guide.md for full step-by-step instructions. Short overview:
1. Launch an Ubuntu EC2 instance.
2. Install Docker & Git.
3. Clone the repo, set production `.env`.
4. Run `docker compose up -d --build`.

Optional: Use Cloudflare Tunnel or Nginx as a reverse proxy and enable TLS.

🔐 Security & Multi-Tenancy
- Google OAuth 2.0 for authentication—no local password storage.
- JWT sessions for stateless, secure API calls.
- Row-Level Security (RLS) and scoping in Pinecone: each user's vectors and chat history are isolated.

🧭 How the RAG Flow Works
1. User logs in with Google → backend issues a JWT.
2. User uploads a document → server splits it into chunks, embeds them, and stores vectors in Pinecone with user_id metadata.
3. On chat query → backend searches Pinecone filtered by user_id, constructs context, and sends to LLM (Groq) for generation.
4. Backend streams the generated tokens back to frontend via WebSocket.

📂 Project Structure
```text
genai-rag-chatbot/
├── backend/            # FastAPI application
│   ├── api/            # API routes (chat, auth, files)
│   ├── database/       # DB models & connection
│   ├── llm/            # Llama 3 & Groq integration
│   └── vectorstore/    # Pinecone integration
├── frontend/           # Next.js application
│   ├── app/            # React pages & components
│   └── public/         # Static assets
└── docker-compose.yml  # Container orchestration
```

⚖️ Trade-offs & Design Decisions
- Latency: Groq LPU enables faster inference for streaming UX.
- Scalability: Containerized Next.js + Docker Compose for portable deployments (Kubernetes later).
- Security: OAuth2 + RLS to ensure tenant isolation and minimize data leakage.
- Cost: Designed to run on modest EC2 instances; Pinecone Starter and Groq free tiers help testing.

🚧 Current Limitations & Roadmap
- Context window limited by Llama 3 (8k tokens). Very large documents may lose detail.
- Only PDF and TXT file types supported; OCR planned for v2.
- Future: monitoring, autoscaling, Kubernetes deployment.

🤝 Contributing
Contributions welcome! Please open issues and pull requests. Branch from `main`, write tests for major changes, and include a clear description.

📄 License
MIT License

---
