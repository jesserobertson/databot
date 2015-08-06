#!/usr/bin/env bash

# Start gunicorn
rm -f gunicorn.log
gunicorn --workers 4 --bind 0.0.0.0:5050 manage:app &> gunicorn.log &
