#!/bin/sh

cd /app

pip install --upgrade pip

apt-get update && apt-get install -y libpq-dev git alsa-utils mpg123 libportaudio2 libportaudiocpp0 portaudio19-dev libasound-dev libsndfile1-dev

pip install --no-cache-dir -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8000
