#!/bin/bash
set -e

# Make script executable
chmod +x render_start.sh

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

# Start server on port 8000
gunicorn fileupload.wsgi:application --bind 0.0.0.0:$PORT 