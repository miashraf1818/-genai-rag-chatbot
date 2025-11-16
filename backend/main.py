from fastapi import FastAPI, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend.vectorstore.pinecone_utils import get_relevant_context
from backend.llm.llama_groq import ask_llama_with_context
from backend.auth.router import router as auth_router
from backend.auth.dependencies import get_current_user
from backend.database.models import User, ChatHistory
from backend.database.connection import get_db

app = FastAPI(
    title="GenAI RAG Chatbot API",
    description="Production-ready RAG chatbot with authentication",
    version="1.0.0"
)

# CORS - Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= INCLUDE ROUTERS =============
# Include authentication router
app.include_router(auth_router)

# Include file upload router
try:
    from backend.api.files import router as files_router
    app.include_router(files_router)
except ImportError:
    print("⚠️ File upload router not found - create backend/api/files.py first")

# Include chat history router
try:
    from backend.api.chat_history import router as chat_history_router
    app.include_router(chat_history_router)
except ImportError:
    print("⚠️ Chat history router not found - create backend/api/chat_history.py first")


@app.get("/")
def root():
    return {
        "message": "GenAI RAG Chatbot API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# ============= WEBSOCKET CHAT (NO AUTH) =============
@app.websocket("/ws/chat")
async def chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat (no auth for now)"""
    await websocket.accept()

    while True:
        try:
            # Receive user query
            user_query = await websocket.receive_text()

            # Get relevant context from Pinecone
            context = get_relevant_context(user_query)

            # Stream response from Llama 3
            for chunk in ask_llama_with_context(user_query, context):
                await websocket.send_text(chunk)

            # Send end signal
            await websocket.send_text("[DONE]")

        except Exception as e:
            await websocket.send_text(f"Error: {str(e)}")
            break


# ============= AUTHENTICATED CHAT WITH HISTORY SAVING =============
@app.post("/api/chat")
async def chat_with_auth(
    query: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Authenticated chat endpoint with history saving
    Requires JWT token in Authorization header
    """
    user_query = query.get("question", "")

    if not user_query:
        return {"error": "Question is required"}

    # Get context from Pinecone
    context = get_relevant_context(user_query)

    # Get response from Llama (collect all chunks)
    response_chunks = []
    for chunk in ask_llama_with_context(user_query, context):
        response_chunks.append(chunk)

    full_response = "".join(response_chunks)

    # ✅ SAVE TO DATABASE
    chat_history = ChatHistory(
        user_id=current_user.id,
        question=user_query,
        answer=full_response,
        context_used=context[:500] if context else None  # Save first 500 chars of context
    )
    db.add(chat_history)
    db.commit()
    db.refresh(chat_history)

    return {
        "id": chat_history.id,
        "question": user_query,
        "answer": full_response,
        "user": current_user.username,
        "timestamp": chat_history.created_at.isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
