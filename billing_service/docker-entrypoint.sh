#!/bin/sh
./wait-for-it.sh billing_db:5432 -t 10 -- echo "postgres is up"
./wait-for-it.sh kafka:9092 -t 15 -- echo "kafka is up"
echo 'Run migration'
python3 manage.py migrate
echo 'Collect Static'
python3 manage.py collectstatic --noinput

echo 'Create super user'
python3 manage.py createsuperuser --noinput

echo 'Sync dj-stripe models'
#python3 manage.py djstripe_sync_models
uwsgi --ini uwsgi.ini
exec "$@"
