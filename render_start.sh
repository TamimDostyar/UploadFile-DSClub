#!/bin/bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Apply database migrations
python3 manage.py migrate

# Collect static files
python3 manage.py collectstatic --noinput

# Start Gunicorn process for production
gunicorn fileupload.wsgi:application --bind 0.0.0.0:$PORT 