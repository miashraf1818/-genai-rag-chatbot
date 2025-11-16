from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from backend.database.connection import get_db
from backend.database.models import User, ChatHistory
from backend.auth.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/chat-history", tags=["Chat History"])


class ChatHistoryResponse(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ChatHistoryResponse])
async def get_chat_history(
        limit: int = 50,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get user's chat history"""

    chats = db.query(ChatHistory) \
        .filter(ChatHistory.user_id == current_user.id) \
        .order_by(ChatHistory.created_at.desc()) \
        .limit(limit) \
        .all()

    return chats


@router.get("/{chat_id}", response_model=ChatHistoryResponse)
async def get_single_chat(
        chat_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get a specific chat by ID"""

    chat = db.query(ChatHistory) \
        .filter(
        ChatHistory.id == chat_id,
        ChatHistory.user_id == current_user.id
    ) \
        .first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    return chat


@router.delete("/{chat_id}")
async def delete_chat(
        chat_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Delete a specific chat"""

    chat = db.query(ChatHistory) \
        .filter(
        ChatHistory.id == chat_id,
        ChatHistory.user_id == current_user.id
    ) \
        .first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    db.delete(chat)
    db.commit()

    return {"message": "Chat deleted successfully"}


@router.delete("/")
async def clear_all_history(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Clear all chat history for current user"""

    deleted_count = db.query(ChatHistory) \
        .filter(ChatHistory.user_id == current_user.id) \
        .delete()

    db.commit()

    return {
        "message": f"Deleted {deleted_count} chat messages",
        "count": deleted_count
    }


@router.get("/stats/summary")
async def get_chat_stats(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get chat statistics for current user"""

    total_chats = db.query(ChatHistory) \
        .filter(ChatHistory.user_id == current_user.id) \
        .count()

    first_chat = db.query(ChatHistory) \
        .filter(ChatHistory.user_id == current_user.id) \
        .order_by(ChatHistory.created_at.asc()) \
        .first()

    last_chat = db.query(ChatHistory) \
        .filter(ChatHistory.user_id == current_user.id) \
        .order_by(ChatHistory.created_at.desc()) \
        .first()

    return {
        "total_chats": total_chats,
        "first_chat_date": first_chat.created_at.isoformat() if first_chat else None,
        "last_chat_date": last_chat.created_at.isoformat() if last_chat else None,
        "user": current_user.username
    }
