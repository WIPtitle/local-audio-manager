#!/bin/sh

cd /app

pip install --upgrade pip

apt-get update && apt-get install -y libpq-dev git pulseaudio libpulse0

echo "default-server = tcp:host.docker.internal:4713" > /etc/pulse/client.conf
echo "autospawn = no" >> /etc/pulse/client.conf

pip install --no-cache-dir -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8000
