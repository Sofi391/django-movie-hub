#!/bin/bash
# Start Celery Worker
celery -A advanced_views worker --loglevel=info --concurrency=1 &

# Start Celery Beat
celery -A advanced_views beat --loglevel=info &

# Start a simple Python server on the assigned Render port
# We use -c to avoid the -m flag since it's causing issues
python -c "import http.server; import os; port = int(os.environ.get('PORT', 10000)); http.server.test(HandlerClass=http.server.SimpleHTTPRequestHandler, port=port)"