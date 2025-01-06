FROM ubuntu:22.04

WORKDIR /app
COPY requirements.txt .
COPY . .

COPY entrypoint.sh /entrypoint.sh
COPY waiting.mp3 /var/lib/local-audio-manager/data/waiting.mp3

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
