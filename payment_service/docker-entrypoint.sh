#!/bin/bash
./wait-for-it.sh db:5432 -t 15 -- echo "postgres is up"
./wait-for-it.sh storage:6379 -t 15 -- echo "storage is up"
cd src

python3 main.py
