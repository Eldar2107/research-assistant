# 1. Node.js vasitəsilə frontend-i build edirik
FROM node:18-slim AS frontend-build
WORKDIR /frontend-app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# 2. Python və FastAPI hissəsi
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Node mərhələsində yaranan dist qovluğunu Python qovluğuna kopyalayırıq
COPY --from=frontend-build /frontend-app/dist /app/frontend/dist

EXPOSE 10000