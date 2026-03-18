#!/bin/bash
set -e
echo "Starting IoT Data Dashboard for Smart Home Management..."
uvicorn app:app --host 0.0.0.0 --port 9036 --workers 1
