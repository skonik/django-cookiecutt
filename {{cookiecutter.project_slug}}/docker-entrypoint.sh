#!/bin/sh

# exit the script if any statement returns a non-true return value.
set -o errexit
# exit in case of uninitialised variable in shell script
set -o nounset

echo ">>> DJANGO_ENV = '${DJANGO_ENV}'"

export LANG='en_US.UTF-8'


if [[ "$1" = "gunicorn" ]] || [[ "$1" = "" ]]; then
    command="cd source && \
    python3 manage.py check && \
    python3 manage.py migrate --no-input && \
    exec gunicorn core.wsgi:application"
elif [[ "$1" = "celery_worker" ]]; then
    command="cd source && \
    python3 manage.py check && \
    exec celery worker --app=core.celery --autoscale=8,1 -P gevent -l INFO"
elif [[ "$1" = "celery_beat" ]]; then
    command="cd source && \
    exec celery beat --app=core.celery -l INFO"
else
    command="exec sh"
fi


eval "${command}"
