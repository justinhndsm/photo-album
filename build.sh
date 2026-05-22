#!/usr/bin/env bash
# Render build script — runs once before the web service starts.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create a superuser non-interactively using env vars.
# Set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL,
# and DJANGO_SUPERUSER_PASSWORD in Render's environment variables.
python manage.py createsuperuser --noinput || true
