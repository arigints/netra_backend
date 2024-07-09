#!/bin/bash

# Start Django development server in the background
python3 manage.py runserver 0.0.0.0:8000 &

# Start Daphne server
daphne -b 0.0.0.0 -p 8002 netra_backend.asgi:application &

# Tail the logs to keep the container running
tail -f /dev/null