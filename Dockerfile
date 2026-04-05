FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY pyproject.lock* ./
COPY evokb/ ./evokb/
COPY README.md .
COPY EVOKB_SCHEMA.md .
COPY config.yaml .
COPY QUICKSTART.md .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create directories
RUN mkdir -p /app/raw /app/wiki /app/clusters

# Create non-root user for security
RUN useradd -m evokb && chown -R evokb:evokb /app
USER evokb

# Expose port
EXPOSE 8000

# Default: Run API server
CMD ["uvicorn", "evokb.api:app", "--host", "0.0.0.0", "--port", "8000"]
