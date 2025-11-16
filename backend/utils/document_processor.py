import os
from typing import List, Dict
from PyPDF2 import PdfReader

# Try to import docx
try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    DocxDocument = None

# Try to import langchain text splitter
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except ImportError:
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        LANGCHAIN_AVAILABLE = False
        RecursiveCharacterTextSplitter = None


class DocumentProcessor:
    """Process and extract text from various document formats"""

    def __init__(self):
        if not LANGCHAIN_AVAILABLE:
            # Fallback: simple manual chunking
            self.text_splitter = None
        else:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )

    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF, DOCX, TXT, MD files"""

        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.pdf':
            return self._extract_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            if not DOCX_AVAILABLE:
                raise ImportError("python-docx not installed. Run: pip install python-docx")
            return self._extract_docx(file_path)
        elif file_ext in ['.txt', '.md']:
            return self._extract_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        doc = DocxDocument(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text

    def _extract_txt(self, file_path: str) -> str:
        """Extract text from TXT/MD"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def split_into_chunks(self, text: str) -> List[str]:
        """Split text into chunks for embedding"""
        if self.text_splitter:
            return self.text_splitter.split_text(text)
        else:
            # Fallback: manual chunking (1000 chars each)
            chunk_size = 1000
            chunks = []
            for i in range(0, len(text), chunk_size):
                chunks.append(text[i:i + chunk_size])
            return chunks

    def process_document(self, file_path: str, metadata: Dict = None) -> List[Dict]:
        """
        Process document: extract text, split into chunks, prepare for embedding
        Returns list of chunk dicts with text and metadata
        """
        # Extract text
        text = self.extract_text(file_path)

        # Split into chunks
        chunks = self.split_into_chunks(text)

        # Prepare chunk dicts with metadata
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_dict = {
                "text": chunk,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "file_path": file_path,
                "file_name": os.path.basename(file_path)
            }

            # Add custom metadata if provided
            if metadata:
                chunk_dict.update(metadata)

            processed_chunks.append(chunk_dict)

        return processed_chunks
