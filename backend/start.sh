#!/bin/bash

RUN_MIGRATIONS=${RUN_MIGRATIONS:-"true"}
STOP_AFTER_MIGRATIONS=${STOP_AFTER_MIGRATIONS:-"false"}
PORT=${PORT:-"8000"}
HOST=${HOST:-"0.0.0.0"}

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running migrations..."
    alembic upgrade head
    if [ "$STOP_AFTER_MIGRATIONS" = "true" ]; then
        echo "Migrations complete. Exiting."
        exit 0
    fi
fi

uvicorn main:app --host "$HOST" --port "$PORT"
