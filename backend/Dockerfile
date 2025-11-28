# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies in a single layer to save space
# We skip apt-get install build-essential/gcc as we rely on wheels.
# If this fails, we might need to add them back, but for now we prioritize disk space.
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
    && sed -i '/torch/d' requirements.txt \
    && pip install --no-cache-dir numpy==2.3.4 pandas==2.3.3 scipy==1.16.3 \
    && pip install --no-cache-dir scikit-learn==1.7.2 \
    && pip install --no-cache-dir transformers==4.57.1 sentence-transformers==5.1.2 \
    && sed -i '/numpy==/d' requirements.txt \
    && sed -i '/pandas==/d' requirements.txt \
    && sed -i '/scipy==/d' requirements.txt \
    && sed -i '/scikit-learn==/d' requirements.txt \
    && sed -i '/transformers==/d' requirements.txt \
    && sed -i '/sentence-transformers==/d' requirements.txt \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
