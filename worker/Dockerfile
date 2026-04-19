# ═══════════════════════════════════════════
#  RepoMind AI — Worker Dockerfile
# ═══════════════════════════════════════════
FROM python:3.11-slim

WORKDIR /app

# Install git for repo cloning
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker source
COPY . .

# Create clone directory
RUN mkdir -p /tmp/repomind-repos

CMD ["python", "main.py"]
