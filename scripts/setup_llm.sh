#!/bin/bash
# Setup Ollama or vLLM for CI testing

set -e

# Check if OLLAMA_BASE_URL is provided (external service)
if [ -n "$OLLAMA_BASE_URL" ]; then
    echo "Using external LLM at: $OLLAMA_BASE_URL"
    exit 0
fi

# Check if vLLM is available
if command -v vllm &> /dev/null; then
    echo "Starting vLLM server..."
    vllm serve --model llama-3.2 --host 0.0.0.0 --port 8000 &
    export OLLAMA_BASE_URL="http://localhost:8000/v1"
    sleep 30
    exit 0
fi

# Try to use Ollama if available
if command -v ollama &> /dev/null; then
    echo "Checking Ollama..."
    if curl -s http://localhost:11434 > /dev/null 2>&1; then
        echo "Ollama already running"
    else
        echo "Starting Ollama..."
        ollama serve &
        sleep 10
    fi
    export OLLAMA_BASE_URL="http://localhost:11434"
    exit 0
fi

echo "No LLM available - tests will use mocks"
