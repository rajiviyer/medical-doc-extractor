#!/bin/bash

# Simple Docker test runner for medical document extractor
# Uses existing docker-compose.yml with profiles

set -e

echo "=== Medical Document Extractor - Docker Testing ==="

case "${1:-help}" in
    "interactive")
        echo "Starting interactive Docker shell..."
        echo "You can run these commands inside the container:"
        echo "  python test_directory_scanner.py"
        echo "  python test_text_extractor.py"
        echo "  python test_document_processor.py"
        echo ""
        docker-compose --profile interactive up --build
        ;;
    "test")
        echo "Running all tests in Docker..."
        docker-compose --profile test run --rm medical-doc-test python test_all_docker.py
        ;;
    "directory")
        echo "Testing directory scanner..."
        docker-compose --profile test run --rm medical-doc-test python test_directory_scanner.py
        ;;
    "extractor")
        echo "Testing text extractor..."
        docker-compose --profile test run --rm medical-doc-test python test_text_extractor.py
        ;;
    "processor")
        echo "Testing document processor..."
        docker-compose --profile test run --rm medical-doc-test python test_document_processor.py
        ;;
    "config")
        echo "Testing LLM configuration..."
        docker-compose --profile test run --rm medical-doc-test python test_llm_config.py
        ;;
    "prompt")
        echo "Testing prompt system..."
        docker-compose --profile test run --rm medical-doc-test python test_prompt_system.py
        ;;
    "build")
        echo "Building Docker image..."
        docker-compose build
        ;;
    "clean")
        echo "Cleaning up..."
        docker-compose down --rmi all --volumes --remove-orphans
        ;;
    "help"|*)
        echo "Usage: $0 [OPTION]"
        echo ""
        echo "Options:"
        echo "  interactive    Start interactive Docker shell"
        echo "  test          Run all tests"
        echo "  directory     Test directory scanner only"
        echo "  extractor     Test text extractor only"
        echo "  processor     Test document processor only"
        echo "  config        Test LLM configuration only"
        echo "  prompt        Test prompt system only"
        echo "  build         Rebuild Docker image"
        echo "  clean         Clean up Docker containers"
        echo "  help          Show this help"
        echo ""
        echo "Examples:"
        echo "  $0 interactive    # Start interactive shell"
        echo "  $0 test          # Run all tests"
        echo "  $0 directory     # Test directory scanner"
        ;;
esac 