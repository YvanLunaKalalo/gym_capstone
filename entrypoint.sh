#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Run Django makemigrations and migrate
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Start the Django server
# Using `runserver` in development; change to `gunicorn` or other WSGI server for production
# python manage.py runserver 0.0.0.0:8000 &

exec gunicorn mysite.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
