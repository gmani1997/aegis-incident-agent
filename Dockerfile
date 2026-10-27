# Use official lightweight Python runtime
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install git and system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code, sandbox targets, and configs
COPY src/ /app/src/
COPY sandbox/ /app/sandbox/
COPY data/ /app/data/
COPY .env.example /app/.env.example

# Expose FastAPI port
EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
