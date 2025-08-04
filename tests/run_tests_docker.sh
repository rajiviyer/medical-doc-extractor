#!/bin/bash

# Docker-based test runner for medical document extractor
# This script runs tests inside Docker to avoid OS conflicts

set -e

echo "=== Medical Document Extractor - Docker Test Runner ==="

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  test              Run all tests with pytest"
    echo "  interactive       Start interactive Docker shell for manual testing"
    echo "  directory         Test directory scanner only"
    echo "  extractor         Test text extractor only"
    echo "  processor         Test document processor only"
    echo "  build             Rebuild Docker image"
    echo "  clean             Clean up Docker containers and images"
    echo "  help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 test           # Run all tests"
    echo "  $0 interactive    # Start interactive shell"
    echo "  $0 directory      # Test directory scanner"
}

# Function to run tests
run_tests() {
    echo "Running tests in Docker..."
    docker-compose -f docker-compose.test.yml --profile test up --build --abort-on-container-exit
}

# Function to start interactive shell
run_interactive() {
    echo "Starting interactive Docker shell..."
    echo "You can run tests manually inside the container:"
    echo "  python test_directory_scanner.py"
    echo "  python test_text_extractor.py"
    echo "  python test_document_processor.py"
    echo ""
    docker-compose -f docker-compose.test.yml --profile interactive up --build
}

# Function to run specific test
run_specific_test() {
    local test_type=$1
    echo "Running $test_type test in Docker..."
    
    case $test_type in
        "directory")
            docker-compose -f docker-compose.test.yml --profile test up --build --abort-on-container-exit -e TEST_SCRIPT="python test_directory_scanner.py"
            ;;
        "extractor")
            docker-compose -f docker-compose.test.yml --profile test up --build --abort-on-container-exit -e TEST_SCRIPT="python test_text_extractor.py"
            ;;
        "processor")
            docker-compose -f docker-compose.test.yml --profile test up --build --abort-on-container-exit -e TEST_SCRIPT="python test_document_processor.py"
            ;;
        *)
            echo "Unknown test type: $test_type"
            show_usage
            exit 1
            ;;
    esac
}

# Function to build Docker image
build_image() {
    echo "Building Docker image..."
    docker-compose -f docker-compose.test.yml build
}

# Function to clean up
clean_up() {
    echo "Cleaning up Docker containers and images..."
    docker-compose -f docker-compose.test.yml down --rmi all --volumes --remove-orphans
    docker system prune -f
}

# Main script logic
case "${1:-help}" in
    "test")
        run_tests
        ;;
    "interactive")
        run_interactive
        ;;
    "directory"|"extractor"|"processor")
        run_specific_test $1
        ;;
    "build")
        build_image
        ;;
    "clean")
        clean_up
        ;;
    "help"|*)
        show_usage
        ;;
esac 