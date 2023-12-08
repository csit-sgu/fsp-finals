#!/usr/bin/sh

if [ ! -f requirements.lock ]; then
    echo "Trying to initialize dependencies..."
    rye sync
fi

docker build -t fsp-backend-base:latest . && docker compose build --parallel
