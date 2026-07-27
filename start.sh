#!/bin/bash
set -e

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

echo "Starting Gunicorn on port ${PORT:-10000}..."
exec gunicorn mvp_project.wsgi:application \
    --bind 0.0.0.0:${PORT:-10000} \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
