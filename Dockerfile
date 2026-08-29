# Dockerfile for NaMo Sovereign Engine (Cloud Run Deployment)
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definitions
COPY pyproject.toml requirements*.txt ./

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

EXPOSE 8080

# Environment defaults
ENV PORT=8080
ENV HOST=0.0.0.0

CMD ["sh", "-c", "python telegram_bot.py & python slack_bot.py & python -m uvicorn server:app --host 0.0.0.0 --port $PORT"]
