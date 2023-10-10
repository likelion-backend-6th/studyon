#! /bin/sh

echo start server

python manage.py collectstatic --no-input
python manage.py migrate

gunicorn config.asgi:application --config config/gunicorn_config.py