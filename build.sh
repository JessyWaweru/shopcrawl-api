#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Convert static files
python manage.py collectstatic --no-input

# Run database migrations (This creates tables in Supabase automatically!)
python manage.py migrate