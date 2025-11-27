# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for psycopg2, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install CPU-only PyTorch (Saves ~3GB disk space)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Safety check: Remove torch from requirements.txt if present to avoid re-installing GPU version
RUN sed -i '/torch==/d' requirements.txt

# Install heavy dependencies individually to prevent "No space left on device"
RUN pip install --no-cache-dir numpy pandas scipy
RUN pip install --no-cache-dir scikit-learn
RUN pip install --no-cache-dir transformers sentence-transformers

# Install remaining Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
