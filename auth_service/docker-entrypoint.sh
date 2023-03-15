#!/bin/bash
./wait-for-it.sh db:5432 -t 15 -- echo "postgres is up"
./wait-for-it.sh storage:6379 -t 15 -- echo "storage is up"
cd src
flask db upgrade
flask create-super-user admin admin admin@admin.com
python3 -m pytest -v -s
python3 pywsgi.py
