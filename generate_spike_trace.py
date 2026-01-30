import json
import random
from datetime import timedelta

# Constants
TOTAL_DURATION = 120  # seconds
SPIKE_STARTS = [90]  # spike start times in seconds
SPIKE_DURATION = 10  # duration of each spike
RPS_STABLE = 1
RPS_SPIKE = 10
INPUT_TOKENS = 2048
OUTPUT_TOKENS = 50
MODEL_NAME = "meta-llama/Llama-3.1-8B"
OUTPUT_PATH = "/mnt/network_drive/lrq/traces/test/rps_spike_2048.json"

# Helper to format timestamp from seconds
def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    microseconds = int((td.total_seconds() - total_seconds) * 1e6)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{microseconds:06}"

# Generate request entry
def generate_request_entry(timestamp):
    data = {
        "data": {
            "model": MODEL_NAME,
            "prompt": [random.randint(0, 10000) for _ in range(INPUT_TOKENS)],
            "temperature": 0,
            "stream": False,
            "max_tokens": OUTPUT_TOKENS,
            "min_tokens": OUTPUT_TOKENS,
        },
        "timestamp": format_timestamp(timestamp)
    }
    return data

# Generate full trace
trace = []
trace.append({"Content-Type": "application/json"})  # HTTP header

current_time = 0.0
while current_time < TOTAL_DURATION:
    # Determine RPS based on time
    in_spike = any(start <= current_time < start + SPIKE_DURATION for start in SPIKE_STARTS)
    rps = RPS_SPIKE if in_spike else RPS_STABLE
    interval = 1.0 / rps

    # Append new request
    trace.append(generate_request_entry(current_time))
    current_time += interval

# Save to JSON file
with open(OUTPUT_PATH, "w") as f:
    json.dump(trace, f)
