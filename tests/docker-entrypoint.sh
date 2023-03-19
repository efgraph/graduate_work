#!/bin/bash

echo "Waiting for API is OK"
python src/utils/api_check.py

pytest -s