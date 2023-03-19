#!/bin/bash
./wait-for-it.sh auth_db:5432 -t 15 -- echo "postgres is up"
./wait-for-it.sh storage:6379 -t 15 -- echo "storage is up"
./wait-for-it.sh kafka:9092 -t 15 -- echo "kafka is up"
cd src
flask db upgrade
flask create-super-user admin admin admin@admin.com
flask create-basic-roles
python3 -m pytest -v -s
python3 pywsgi.py