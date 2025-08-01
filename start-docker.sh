#!/bin/bash

# Default values
PROFILE="main"
BUILD=false
NO_CACHE=false

# Parse command line arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --main)
            PROFILE="main"
            shift
            ;;
        --test)
            PROFILE="test"
            shift
            ;;
        --interactive)
            PROFILE="interactive"
            shift
            ;;
        --build)
            BUILD=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Profile Options:"
            echo "  --main         Start main application service (default)"
            echo "  --test         Start test service"
            echo "  --interactive  Start interactive development service"
            echo ""
            echo "Build Options:"
            echo "  --build        Build images before starting"
            echo "  --no-cache     Build without cache"
            echo "  --help         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Start main service"
            echo "  $0 --main --build     # Start main service with build"
            echo "  $0 --test             # Start test service"
            echo "  $0 --interactive      # Start interactive service"
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

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose down
sleep 2

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

echo ""
echo "✅ Docker services started successfully!"
echo ""
echo "Useful commands:"
echo "  View logs:     docker-compose --profile $PROFILE logs -f"
echo "  Stop services: docker-compose down"
echo "  Access shell:  docker-compose --profile $PROFILE exec medical-rag-pipeline bash"
echo ""
echo "Profile: $PROFILE"
case $PROFILE in
    "main")
        echo "Service: medical-rag-pipeline (Main application)"
        echo "Usage: docker-compose run --rm medical-rag-pipeline python app/main.py"
        ;;
    "test")
        echo "Service: medical-doc-test (Testing service)"
        echo "Usage: ./test_docker.sh test"
        ;;
    "interactive")
        echo "Service: medical-doc-interactive (Interactive development)"
        echo "Usage: docker-compose --profile interactive exec medical-doc-interactive bash"
        ;;
esac 