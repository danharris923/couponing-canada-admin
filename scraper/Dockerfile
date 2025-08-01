FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scraper code
COPY . .

# Create volume for credentials
VOLUME ["/app/credentials"]

# Default command runs the scraper
CMD ["python", "savingsguru_scraper.py"]