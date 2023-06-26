#!/bin/sh

if [ "$START" = "collect" ] || [ "$START" = "all" ]; then
  echo "=== Collect static files ==="
  python manage.py collectstatic --noinput
fi

if [ "$START" = "migrate" ] || [ "$START" = "all" ]; then
  echo ""
  echo "=== Apply database migrations ==="
  /wait-for-it.sh db:5432 -- python manage.py migrate
fi

gunicorn foodgram.wsgi:application --bind 0:8000