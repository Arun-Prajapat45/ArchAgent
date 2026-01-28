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
    && rm -rf /var/lib/apt/lists/*

# ---- Working directory ----
WORKDIR /app

# ---- Upgrade pip ----
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
    langchain-google-genai \
    langgraph

# ---- Default command ----
CMD ["bash"]
