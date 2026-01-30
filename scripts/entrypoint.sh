#!/bin/bash
set -e

if [ "$QUERY_PROM" != "0" ]; then
  echo "Starting Prometheus..."
  /prometheus/prometheus \
    --storage.tsdb.path="$SNAPSHOT" \
    --config.file=/prometheus/prometheus.yml &
  sleep 10
else
  echo "QUERY_PROM is 0, skipping Prometheus startup."
fi

echo "Running Python app..."
python3 /app/main.py