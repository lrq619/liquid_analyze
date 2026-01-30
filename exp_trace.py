#!/usr/bin/env python3
import json
import random
from datetime import timedelta

dst_trace_path = "/mnt/network_drive/lrq/traces/exp/exp.json"

# Parameters
duration_sec = 120           # total duration = 1 minute
rps = 1                     # stable traffic: 1 request per second
stable_input = 1024         # stable prompt length
stable_output = 4          # stable output length
spike_time = 90             # spike at second 30
spike_count = 10            # number of spike requests
spike_input = 8192         # spike prompt length
spike_output = 4           # spike output length

# === Helper functions ===
def format_timestamp(td: timedelta) -> str:
    """Format timedelta as HH:MM:SS.microseconds with always 6 digits."""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    micros = td.microseconds
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{micros:06d}"

def generate_request(ts: timedelta, prompt_len: int, output_len: int):
    prompt = [random.randint(1, 32000) for _ in range(prompt_len)]
    return {
        "data": {
            "model": "meta-llama/Llama-3.1-8B",
            "prompt": prompt,
            "max_tokens": output_len,
            "min_tokens": output_len,
            "temperature": 0,
            "stream": False
        },
        "timestamp": format_timestamp(ts)
    }

# === Build trace ===
trace = [{"Content-Type": "application/json"}]

# Stable traffic (1 request per second)
for sec in range(duration_sec):
    ts = timedelta(seconds=sec)
    trace.append(generate_request(ts, stable_input, stable_output))

# Spike traffic (10 requests between 30s and 31s)
for i in range(spike_count):
    # distribute them evenly in [30s, 31s)
    offset = i * (1_000_000 // spike_count)  # microseconds
    ts = timedelta(seconds=spike_time, microseconds=offset)
    trace.append(generate_request(ts, spike_input, spike_output))

# === Sort by timestamp (so spike requests mix correctly at ~30s) ===
trace_with_header = [trace[0]] + sorted(trace[1:], key=lambda r: r["timestamp"])

# === Write to file ===
with open(dst_trace_path, "w") as f:
    json.dump(trace_with_header, f, indent=2)

print(f"Trace written to {dst_trace_path}")
print(f"Total requests: {len(trace_with_header) - 1} (including {spike_count} spike requests)")
