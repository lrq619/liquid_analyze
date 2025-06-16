#!/bin/bash
set -e

echo "Starting Prometheus..."
/prometheus/prometheus \
  --storage.tsdb.path="$SNAPSHOT" \
  --config.file=/prometheus/prometheus.yml &

sleep 10

echo "Running Python app..."
python3 /app/main.py