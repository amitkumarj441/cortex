#!/usr/bin/env bash
export DJANGO_SETTINGS_MODULE="worldbrain.settings.development"
export DJANGO_SECRET_KEY=0123456789abcdefghijklmnopqrstuvwyxz
export DATABASE_NAME=worldbrain
export DATABASE_USER=cortex
export DATABASE_PASSWORD=cortex
export ES_HOST=127.0.0.1:9200
export PGHOST=localhost
python -m worldbrain.cortex.deamons.spider