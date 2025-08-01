#!/bin/bash

# Default values
BUILD=false
NO_CACHE=false
PROFILE="main"

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
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --build        Build images before starting"
            echo "  --no-cache     Build without cache"
            echo "  --profile NAME Specify profile (main, test, interactive)"
            echo "  --help         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "Starting Docker services with profile: $PROFILE"

# Stop containers
echo "Stopping existing containers..."
docker-compose down
sleep 3

# Start containers with appropriate options
if [ "$BUILD" = "true" ]; then
    if [ "$NO_CACHE" = "true" ]; then
        echo "Building images without cache..."
        docker-compose --profile $PROFILE build --no-cache
        echo "Starting services..."
        docker-compose --profile $PROFILE up -d
    else
        echo "Building and starting services..."
        docker-compose --profile $PROFILE up --build -d
    fi
else
    echo "Starting services..."
    docker-compose --profile $PROFILE up -d
fi

echo "Docker services started successfully!"
echo "To view logs: docker-compose --profile $PROFILE logs -f"
echo "To stop services: docker-compose down"