# EvoKB CLI Usage Guide

## Quick Start

```bash
# Setup
chmod +x setup.sh test.sh autoreview.sh
./setup.sh

# Activate virtual environment
source .venv/bin/activate
```

## Commands

### Start Librarian (Autoreview Loop)

```bash
# Using shell script
./autoreview.sh

# Or with custom iterations
./autoreview.sh 5 20  # 5 iterations, 20s interval

# Using Python directly
python run_autoreview.py -n 3 -i 30 -e
```

### Run Tests

```bash
# Test accuracy
./test.sh

# Or
python test_accuracy.py

# Run all unit tests
pytest tests/
```

### Start API Server

```bash
evokb-api
# or
python -m evokb.api
```

### Scrape a Website

```bash
python -m evokb.scraper <url> [output_dir]
```

## CLI Scripts

| Script | Purpose |
|--------|---------|
| `setup.sh` | Initial setup and install |
| `test.sh` | Run accuracy tests |
| `autoreview.sh` | Run autoreview loop |

## Options

### run_autoreview.py Options

```
-n, --iterations    Number of iterations (default: 5)
-i, --interval     Seconds between iterations (default: 30)
-e, --eval         Run evaluation after
-c, --compile      Compile raw files before starting
```

### test_accuracy.py

Runs Q&A and search accuracy tests against the knowledge base.

## Examples

```bash
# Quick test
./test.sh

# Run 3 improvement cycles
./autoreview.sh 3

# Run with evaluation
python run_autoreview.py -n 5 -e
```
