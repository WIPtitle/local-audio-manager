#!/bin/sh

cd /app

apt update && apt-get install -y python3-pip libpq-dev git alsa-utils mpg123 libportaudio2 libportaudiocpp0 portaudio19-dev libasound-dev libsndfile1-dev

pip3 install --upgrade pip
pip3 install --no-cache-dir -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8000
