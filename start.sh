#!/bin/bash
set -e

echo "=== Starting deployment ==="
echo "PORT: ${PORT:-10000}"

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Creating superuser if not exists..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin1234')
    print('Superuser created: admin / admin1234')
else:
    print('Superuser already exists')
"

echo "Configuring Nginx..."
export PORT=${PORT:-10000}
envsubst '${PORT}' < /etc/nginx/nginx.conf > /etc/nginx/nginx.conf.tmp
mv /etc/nginx/nginx.conf.tmp /etc/nginx/nginx.conf

echo "Starting Gunicorn on internal port 8001..."
gunicorn mvp_project.wsgi:application \
    --bind 127.0.0.1:8001 \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - &

echo "Waiting for Gunicorn to start..."
sleep 3

echo "Starting Nginx on port ${PORT}..."
nginx -g 'daemon off;'
