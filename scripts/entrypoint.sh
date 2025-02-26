#!/bin/bash

echo "Applying database migrations..."
uv run manage.py migrate

echo "Starting server..."
exec "$@"
