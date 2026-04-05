FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for tantivy
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY evokb/ ./evokb/
COPY README.md .
COPY EVOKB_SCHEMA.md .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create directories
RUN mkdir -p /app/raw /app/wiki /app/clusters

# Expose port
EXPOSE 8000

# Run the API server by default
CMD ["uvicorn", "evokb.api:app", "--host", "0.0.0.0", "--port", "8000"]
