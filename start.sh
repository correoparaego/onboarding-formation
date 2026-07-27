#!/bin/bash
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn and Nginx..."

# Start Gunicorn in background
gunicorn mvp_project.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - &

# Start Nginx in foreground
nginx -g 'daemon off;'
