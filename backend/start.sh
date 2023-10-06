#!/bin/bash

set -e

RUN_MIGRATIONS=${RUN_MIGRATIONS:-"true"}
STOP_AFTER_MIGRATIONS=${STOP_AFTER_MIGRATIONS:-"false"}
MIGRATION_DOWNGRADE_VERSION=${MIGRATION_DOWNGRADE_VERSION:-""}
PORT=${PORT:-"8000"}
HOST=${HOST:-"0.0.0.0"}

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running migrations..."
    if [ "$MIGRATION_DOWNGRADE_VERSION" != "" ]; then
        echo "Downgrading to version $MIGRATION_DOWNGRADE_VERSION"
        alembic downgrade "$MIGRATION_DOWNGRADE_VERSION"
    else 
        alembic upgrade head
        if [ "$STOP_AFTER_MIGRATIONS" = "true" ]; then
            echo "Migrations complete. Exiting."
            exit 0
        fi
    fi
fi

uvicorn main:app --host "$HOST" --port "$PORT"
