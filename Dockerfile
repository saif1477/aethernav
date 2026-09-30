# Multi-stage Dockerfile for AetherNav GNSS-Denied Navigation Research Pipeline

FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy package metadata first for efficient caching
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install python dependencies and package in editable mode
RUN pip install --upgrade pip setuptools wheel && \
    pip install -e '.[dev,ml]' || pip install -e '.[dev]'

# Copy rest of codebase
COPY . .

# Ensure sample dataset exists
RUN python scripts/create_sample_dataset.py --output data/sample/demo.csv

EXPOSE 8000

# Default command runs evaluation pipeline and test suite
CMD ["python", "scripts/evaluate.py", "--config", "configs/demo.yaml"]
