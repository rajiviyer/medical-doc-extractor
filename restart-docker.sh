#!/bin/bash

# Default values
BUILD=false
NO_CACHE=false

# Parse command line arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --build)
            BUILD=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Stop containers
docker-compose down
sleep 3

# Start containers with appropriate options
if [ "$BUILD" = "true" ]; then
    if [ "$NO_CACHE" = "true" ]; then
        docker-compose build --no-cache
        docker-compose up -d
    else
        docker-compose up --build -d
    fi
else
    docker-compose up -d
fi