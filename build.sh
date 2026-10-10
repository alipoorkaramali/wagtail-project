#!/usr/bin/env bash
# Render build script for Wagtail + MCP app

set -o errexit  # exit on error

echo "==> Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Running migrations..."
python manage.py migrate --no-input

echo "==> Build complete!"
