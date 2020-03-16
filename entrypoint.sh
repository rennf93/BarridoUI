#!/bin/sh

set -eoux pipefail

if [ "$1" == 'celery_worker' ]; then
    celery worker -A barridoUI.celery:app -c 4 -l info
elif [ "$1" == 'celery_beat' ]; then
    celery beat -A barridoUI.celery:app -l info
elif [ "$1" == 'flower_worker' ]; then
    celery flower -A barridoUI.celery:app -l info
elif [ "$1" == 'flower_and_worker' ]; then
    python health.py &
    celery flower -A barridoUI.celery:app -l info --address=0.0.0.0 --port=9091 &
    celery worker -A barridoUI.celery:app -c 4 -l info
else
    python manage.py makemigrations --noinput
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput
    python manage.py loaddata core/fixtures/*
fi
