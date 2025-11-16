from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List
import os
import uuid
from datetime import datetime
from backend.auth.dependencies import get_current_user
from backend.database.models import User
from backend.utils.document_processor import DocumentProcessor
from backend.vectorstore.document_indexer import document_indexer

router = APIRouter(prefix="/files", tags=["File Upload"])

# File storage directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.doc', '.docx', '.md'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Initialize document processor
doc_processor = DocumentProcessor()


@router.post("/upload")
async def upload_file(
        file: UploadFile = File(...),
        process_for_rag: bool = True,  # NEW: Enable RAG processing by default
        current_user: User = Depends(get_current_user)
):
    """Upload and optionally process file for RAG"""

    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read file content
    content = await file.read()

    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Generate unique filename and document ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    document_id = str(uuid.uuid4())
    safe_filename = f"{current_user.id}_{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    response_data = {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "size": len(content),
        "path": file_path,
        "document_id": document_id
    }

    # ✅ PROCESS FOR RAG
    if process_for_rag:
        try:
            # Extract text and split into chunks
            chunks = doc_processor.process_document(
                file_path,
                metadata={
                    "user_id": current_user.id,
                    "username": current_user.username
                }
            )

            # Index into Pinecone
            index_result = document_indexer.index_document_chunks(
                chunks=chunks,
                user_id=current_user.id,
                document_id=document_id
            )

            response_data["rag_processing"] = {
                "status": "success",
                "chunks_indexed": index_result["chunks_indexed"],
                "document_id": index_result["document_id"],
                "message": f"✅ Document processed! {index_result['chunks_indexed']} chunks indexed for AI search."
            }

        except Exception as e:
            response_data["rag_processing"] = {
                "status": "failed",
                "error": str(e),
                "message": "⚠️ File uploaded but RAG processing failed. File is still saved."
            }

    return response_data


@router.post("/upload-multiple")
async def upload_multiple_files(
        files: List[UploadFile] = File(...),
        process_for_rag: bool = True,
        current_user: User = Depends(get_current_user)
):
    """Upload multiple files"""

    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files at once")

    results = []

    for file in files:
        try:
            # Call the single upload function
            result = await upload_file(file, process_for_rag, current_user)
            results.append({"filename": file.filename, "status": "success", **result})
        except HTTPException as e:
            results.append({"filename": file.filename, "status": "failed", "error": str(e.detail)})

    return {"results": results, "total_files": len(files)}


@router.get("/list")
async def list_user_files(current_user: User = Depends(get_current_user)):
    """List all files uploaded by current user"""

    user_files = []

    if not os.path.exists(UPLOAD_DIR):
        return {"files": [], "count": 0}

    for filename in os.listdir(UPLOAD_DIR):
        if filename.startswith(f"{current_user.id}_"):
            file_path = os.path.join(UPLOAD_DIR, filename)
            file_stat = os.stat(file_path)

            user_files.append({
                "filename": filename.split("_", 2)[2],  # Remove user_id and timestamp
                "size": file_stat.st_size,
                "uploaded_at": datetime.fromtimestamp(file_stat.st_ctime).isoformat()
            })

    return {"files": user_files, "count": len(user_files)}


@router.delete("/delete/{filename}")
async def delete_file(
        filename: str,
        current_user: User = Depends(get_current_user)
):
    """Delete a specific file"""

    # Find the actual file with user_id prefix
    actual_filename = None
    for f in os.listdir(UPLOAD_DIR):
        if f.startswith(f"{current_user.id}_") and f.endswith(filename):
            actual_filename = f
            break

    if not actual_filename:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = os.path.join(UPLOAD_DIR, actual_filename)

    try:
        os.remove(file_path)
        return {
            "message": "File deleted successfully",
            "filename": filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
