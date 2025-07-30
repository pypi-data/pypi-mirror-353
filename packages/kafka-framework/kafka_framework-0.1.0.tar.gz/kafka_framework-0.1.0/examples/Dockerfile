FROM python:3.10-slim

# Environment configuration
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gcc \
    libffi-dev \
    unzip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv (official script writes to /usr/local/bin)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh -s -- -b /usr/local/bin

# Copy project files
COPY . /app

# Install dependencies with dev extras
RUN uv sync --extras dev

# Set working directory to examples
WORKDIR /app/examples

# Run the app
CMD ["python", "app.py"]
