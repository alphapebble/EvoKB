# EvoKB Deployment Guide

## Quick Start with Docker

### Build and Run

```bash
# Build the image
docker build -t evokb:latest .

# Run the API server
docker run -p 8000:8000 evokb:latest

# Run the Librarian (auto-compiles raw -> wiki)
docker run -v /path/to/raw:/app/raw -v /path/to/wiki:/app/wiki evokb:latest python -m evokb.agents.librarian
```

### Using Docker Compose

```bash
# Start API server only
docker-compose up api

# Start with Librarian (auto-compiles)
docker-compose up librarian

# Start everything (API + Librarian + Ollama)
docker-compose --profile ollama up
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Model settings
MODEL=ollama/llama3.2
OLLAMA_BASE_URL=http://localhost:11434

# Gmail Connector
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Notion Connector
NOTION_API_KEY=

# Slack/Discord
SLACK_BOT_TOKEN=
DISCORD_BOT_TOKEN=
```

### Volume Mounts

| Path | Description |
|------|-------------|
| `/app/raw` | Source documents to ingest |
| `/app/wiki` | Compiled knowledge base |
| `/app/clusters` | Knowledge clusters |

### Example: Full Stack

```bash
# 1. Start Ollama
docker-compose --profile ollama up -d

# 2. Start API
docker-compose up api -d

# 3. Start Librarian
docker-compose up librarian -d

# 4. Check health
curl http://localhost:8000/health

# 5. Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is a knowledge graph?"}'
```

### Production Deployment

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./wiki:/app/wiki
      - ./clusters:/app/clusters
    environment:
      - MODEL=ollama/llama3.2
      - OLLAMA_BASE_URL=http://ollama:11434
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  ollama:
    image: ollama/ollama:latest
    restart: always
    volumes:
      - ollama_data:/root/.ollama

volumes:
  ollama_data:
```

```bash
# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Troubleshooting

```bash
# Check logs
docker-compose logs -f

# Restart services
docker-compose restart

# Check health
docker-compose ps

# Access container shell
docker-compose exec api sh
```

## Local Development (without Docker)

```bash
git clone https://github.com/alphapebble/evokb.git
cd evokb
pip install -e .
mkdir -p raw wiki clusters
python -m evokb.agents.librarian
```

See QUICKSTART.md for more details.
