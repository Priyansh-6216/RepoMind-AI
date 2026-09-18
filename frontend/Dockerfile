# ═══════════════════════════════════════════
#  RepoMind AI — Frontend Dockerfile
# ═══════════════════════════════════════════

# Stage 1: Build
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve (Non-root)
FROM nginxinc/nginx-unprivileged:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Nginx config for SPA routing (needs to go to a path the unprivileged user can write to if modifying, but we can just use the default drop-in)
USER root
RUN echo 'server { \
    listen 3000; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location /api { \
        proxy_pass http://backend:8080; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Switch back to non-root user
USER nginx

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
