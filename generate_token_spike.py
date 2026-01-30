import json
import random
from datetime import timedelta

# Constants
TOTAL_DURATION = 120  # seconds
SPIKE_STARTS = [90]  # spike start times in seconds
SPIKE_DURATION = 10  # duration of each spike
RPS_STABLE = 1
INPUT_TOKENS = 2048
OUTPUT_TOKENS = 50
MODEL_NAME = "meta-llama/Llama-3.1-8B"
OUTPUT_PATH = "/mnt/network_drive/lrq/traces/test/token_spike_2048.json"

# Helper to format timestamp from seconds
def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    microseconds = int((td.total_seconds() - total_seconds) * 1e6)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{microseconds:06}"

# Generate request entry
def generate_request_entry(timestamp, input_tokens, output_tokens):
    data = {
        "data": {
            "model": MODEL_NAME,
            "prompt": [random.randint(0, 10000) for _ in range(input_tokens)],
            "temperature": 0,
            "stream": False,
            "max_tokens": output_tokens,
            "min_tokens": output_tokens,
        },
        "timestamp": format_timestamp(timestamp)
    }
    return data

# Generate full trace
trace = []
trace.append({"Content-Type": "application/json"})  # HTTP header

current_time = 0.0
while current_time < TOTAL_DURATION:
    # Determine if we're in a spike
    in_spike = any(start <= current_time < start + SPIKE_DURATION for start in SPIKE_STARTS)
    
    # Keep RPS constant, change token length during spike
    input_tokens = INPUT_TOKENS * 5 if in_spike else INPUT_TOKENS
    output_tokens = OUTPUT_TOKENS * 5 if in_spike else OUTPUT_TOKENS
    interval = 1.0 / RPS_STABLE

    # Append new request
    trace.append(generate_request_entry(current_time, input_tokens, output_tokens))
    current_time += interval

# Save to JSON file
with open(OUTPUT_PATH, "w") as f:
    json.dump(trace, f)