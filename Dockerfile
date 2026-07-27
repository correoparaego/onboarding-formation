# Multi-stage build: frontend + backend
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# Production stage
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=mvp_project.settings

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Copy built frontend assets
COPY --from=frontend-build /app/frontend/dist /app/staticfiles/frontend

# Collect Django static files
RUN python manage.py collectstatic --noinput || true

# Copy startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose port (Render asigna PORT dinámicamente)
EXPOSE 10000

# Start Gunicorn
CMD ["/start.sh"]
