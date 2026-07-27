#!/bin/bash
# Render build script for backend

set -o errexit
set -o pipefail
set -o nounset

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Build completed successfully!"
