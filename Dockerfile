FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev git curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY waiting.mp3 /var/lib/local-audio-manager/data/waiting.mp3

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
