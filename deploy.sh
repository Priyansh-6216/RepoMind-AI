#!/usr/bin/env bash
# ══════════════════════════════════════════════
#  RepoMind AI — Production Deployment Script
# ══════════════════════════════════════════════
set -e

echo "🚀 Starting RepoMind AI Deployment..."

# 1. Pull latest code
echo "📦 Pulling latest changes from main branch..."
git fetch origin main
git reset --hard origin/main

# 2. Setup Env Vars
if [ ! -f .env ]; then
    echo "⚠️  .env file not found! Creating from .env.example..."
    cp .env.example .env
    echo "❗ Please review .env file to ensure production secrets are set."
fi

# 3. Build and restart containers
echo "🏗️  Building and recreating Docker containers..."
export SPRING_PROFILES_ACTIVE=prod
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up -d --remove-orphans

# 4. Clean up dangling images
echo "🧹 Cleaning up unused Docker images..."
docker image prune -f

echo "✅ Deployment completed successfully!"
docker-compose ps
