#!/bin/bash
./wait-for-it.sh kafka:9092 -t 15 -- echo "kafka is up"
set -o errexit
set -o pipefail
set -o nounset

cd src
python3 consume.py
