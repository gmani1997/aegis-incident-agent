# Use official lightweight Python runtime
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=8080

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/src/
COPY sandbox/ /app/sandbox/
COPY data/ /app/data/
COPY .env.example /app/.env.example

EXPOSE 8080

# Use shell form to dynamically respect Cloud Run $PORT (defaults to 8080)
CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8080}
