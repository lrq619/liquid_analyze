#!/bin/bash
set -e

# Define the target directory for restoring the snapshot
RESTORE_DIR="/app/prometheus_restore"

# Ensure the directory exists and is empty
mkdir -p "$RESTORE_DIR"
rm -rf "$RESTORE_DIR"/*

# Copy the snapshot to /app before restoring
echo "Copying Prometheus snapshot from $SNAPSHOT to $RESTORE_DIR..."
cp -r "$SNAPSHOT"/* "$RESTORE_DIR"

if [ "$QUERY_PROM" != "0" ]; then
  echo "Starting Prometheus from restored snapshot..."
  /prometheus/prometheus \
    --storage.tsdb.path="$RESTORE_DIR" \
    --config.file=/prometheus/prometheus.yml &
  sleep 10
else
  echo "QUERY_PROM is 0, skipping Prometheus startup."
fi

echo "Running Python app..."
python3 /app/main.py