FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing bytecode and enable bufferless output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies required for building C extensions and downloading assets
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies list and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Download spaCy English model for Presidio PII analyzer
RUN python -m spacy download en_core_web_sm || true

# Copy project files into container
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Run main application
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
