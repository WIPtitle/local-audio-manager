FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY waiting.mp3 /var/lib/local-audio-manager/data/waiting.mp3

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
