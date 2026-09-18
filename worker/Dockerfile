# ═══════════════════════════════════════════
#  RepoMind AI — Worker Dockerfile
# ═══════════════════════════════════════════
# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runner (Non-root)
FROM python:3.11-slim
WORKDIR /app

# Install git
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r workergroup && useradd -r -g workergroup workeruser

# Copy dependencies from builder
COPY --from=builder /root/.local /home/workeruser/.local

# Copy worker source
COPY . .

# Set permissions for clone directory
RUN mkdir -p /tmp/repomind-repos && chown -R workeruser:workergroup /tmp/repomind-repos /app

# Switch to non-root user
USER workeruser
ENV PATH=/home/workeruser/.local/bin:$PATH

CMD ["python", "main.py"]
