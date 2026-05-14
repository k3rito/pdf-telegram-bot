# syntax=docker/dockerfile:1.7

FROM python:3.11-slim AS builder
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc g++ libc-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && pip wheel --wheel-dir=/wheels -r requirements.txt

FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

RUN useradd --create-home --shell /bin/bash pdfbot \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-ara \
        tesseract-ocr-eng \
        poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir /wheels/*

COPY . .
RUN chown -R pdfbot:pdfbot /app
USER pdfbot

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 CMD python -c "import sys; sys.exit(0)"
CMD ["python", "bot.py"]
