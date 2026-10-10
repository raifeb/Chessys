FROM python:3.12-slim

# Install system utilities needed for downloading and running Stockfish
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Pinned official Stockfish 17 Linux AVX2 release
ARG STOCKFISH_URL=https://github.com/official-stockfish/Stockfish/releases/download/sf_17/stockfish-ubuntu-x86-64-avx2.tar
ARG STOCKFISH_SHA256=6c9aaaf4c7db0f6934a5f7c29a06172f9d22c1e6db68dfdf22f69ae60341cdde

RUN mkdir -p /app/bin && \
    curl -sSL "$STOCKFISH_URL" -o /tmp/stockfish.tar && \
    echo "$STOCKFISH_SHA256  /tmp/stockfish.tar" | sha256sum -c - && \
    tar -xf /tmp/stockfish.tar -C /tmp && \
    cp /tmp/stockfish/stockfish-ubuntu-x86-64-avx2 /app/bin/stockfish && \
    chmod +x /app/bin/stockfish && \
    rm -rf /tmp/stockfish*

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install Python dependencies first for optimal Docker layer caching
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend application source and model artifacts
COPY --chown=appuser:appuser backend/ /app/

USER appuser

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

