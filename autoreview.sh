#!/bin/bash
# Run EvoKB autoreview loop

cd "$(dirname "$0")"

source .venv/bin/activate 2>/dev/null || true

# Default: run 3 iterations with 30s interval
ITERATIONS=${1:-3}
INTERVAL=${2:-30}

echo "Running autoreview loop..."
echo "Iterations: $ITERATIONS"
echo "Interval: ${INTERVAL}s"
echo ""

python3 run_autoreview.py -n $ITERATIONS -i $INTERVAL -e
