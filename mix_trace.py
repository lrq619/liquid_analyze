conv_trace_path = "/mnt/network_drive/lrq/traces/conv/sample_0_all_input1_output1_ids.json"
code_trace_path = "/mnt/network_drive/lrq/traces/code/sample_0_all_input1_output1_ids_upsample_2.json"
burst_trace_path = "/mnt/network_drive/lrq/traces/burst/burst_gpt_1_upsample_2.json"
out_path = "/mnt/network_drive/lrq/traces/mixed/mixed.json"

# downsample conv trace by 50%
#!/usr/bin/env python3
import json
import random
from tqdm import tqdm

# Fixed file paths
downsample_ratio = 0.5
seed = 42  # fix for reproducibility
random.seed(seed)


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def write_json_compact(path, data):
    with open(path, "w") as f:
        json.dump(data, f, separators=(",", ":"))


# === Load traces ===
files = [("conv", conv_trace_path), ("code", code_trace_path), ("burst", burst_trace_path)]
data = {}
for name, p in tqdm(files, desc="Loading trace files"):
    data[name] = load_json(p)
    tqdm.write(f"Loaded {name}: {p}, total entries: {len(data[name])}")

# Extract header and requests
header = data["conv"][0]
conv_requests = data["conv"][1:]
code_requests = data["code"][1:] if len(data["code"]) > 1 else []
burst_requests = data["burst"][1:] if len(data["burst"]) > 1 else []

# === Downsample conv ===
total_conv = len(conv_requests)
keep_count = int(total_conv * downsample_ratio)

tqdm.write(f"Conv original requests: {total_conv}, keeping {keep_count}")

selected_indices = sorted(random.sample(range(total_conv), keep_count))
conv_downsampled = [conv_requests[i] for i in selected_indices]

# === Build mixed trace ===
mixed_requests = []
for req in tqdm(conv_downsampled, desc="Appending conv"):
    mixed_requests.append(req)
for req in tqdm(code_requests, desc="Appending code"):
    mixed_requests.append(req)
for req in tqdm(burst_requests, desc="Appending burst"):
    mixed_requests.append(req)

final_trace = [header] + mixed_requests

# === Save result ===
write_json_compact(out_path, final_trace)

print("=== Summary ===")
print(f"Conv kept: {len(conv_downsampled)} / {total_conv}")
print(f"Code kept: {len(code_requests)}")
print(f"Burst kept: {len(burst_requests)}")
print(f"Final mixed file: {out_path}, total length: {len(final_trace)}")
