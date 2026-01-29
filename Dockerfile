# ---- Base image ----
FROM python:3.12-slim

# ---- Environment settings ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# ---- System dependencies ----
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel

# ---- Core Python packages ----
RUN pip install \
    python-dotenv \
    pydantic \
    requests \
    tiktoken \
    langchain \
    langchain-core \
    langchain-community \
    langgraph \
    fastapi \
    uvicorn \
    psycopg[binary] \
    psycopg-pool \
    fastapi[standard] \
    faiss-cpu \
    langchain-openai  

COPY . .

CMD ["fastapi", "dev", "backend/app.py", "--host", "0.0.0.0", "--port", "8000"]