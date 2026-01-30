import json
import random
import copy
import argparse
from datetime import datetime

class RequestStatus:
    def __init__(self, arrival_time, prefill_length, decode_length, prompt, raw_json):
        self.arrival_time = arrival_time
        self.prefill_length = prefill_length
        self.decode_length = decode_length
        self.prompt = prompt
        self.raw_json = raw_json  # keep full original JSON

def timestamp_str_to_seconds(ts_str):
    t = datetime.strptime(ts_str, "%H:%M:%S.%f")
    return t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1e6

def seconds_to_timestamp_str(seconds: float) -> str:
    """Convert seconds (float) into format H:MM:SS.ffffff"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    micros = int(round((seconds - int(seconds)) * 1e6))
    return f"{hours}:{minutes:02d}:{secs:02d}.{micros:06d}"

def main(trace_file_path: str, sweep_ratio: int):
    dst_trace_file_path = trace_file_path.replace(".json", f"_upsample_{sweep_ratio}.json")

    # load the trace file
    requests = []
    with open(trace_file_path, 'r') as f:
        trace_json_data = json.load(f)
        for req_json in trace_json_data[1:]:
            arrival_timestamp = timestamp_str_to_seconds(req_json['timestamp'])
            data = req_json['data']
            prefill_length = len(data['prompt'])
            decode_length = data['max_tokens']
            request_stat = RequestStatus(
                arrival_time=arrival_timestamp,
                prefill_length=prefill_length,
                decode_length=decode_length,
                prompt=data['prompt'],
                raw_json=req_json  # keep the full request structure
            )
            requests.append(request_stat)

    # Build new requests list (original + multiplexed)
    upsampled_requests = []

    for req in requests:
        # Original request (deep copy to preserve structure)
        orig_copy = copy.deepcopy(req.raw_json)
        upsampled_requests.append(orig_copy)

        # Multiplex extra requests, shifted by 10ms, 20ms, ...
        for k in range(1, sweep_ratio):
            new_copy = copy.deepcopy(req.raw_json)

            shuffled_prompt = req.prompt[:]
            # ensure shuffle produces a different sequence
            attempts = 0
            while True:
                random.shuffle(shuffled_prompt)
                attempts += 1
                if shuffled_prompt != req.prompt:
                    break
                if attempts > 10:  # safeguard
                    print("Warning: shuffle failed to change prompt")
                    break

            shifted_time = req.arrival_time + k * 0.010  # shift by k*10ms
            new_copy["timestamp"] = seconds_to_timestamp_str(shifted_time)
            new_copy["data"]["prompt"] = shuffled_prompt
            upsampled_requests.append(new_copy)

    # Sort by timestamp (important if strict chronological order is needed)
    upsampled_requests.sort(key=lambda r: timestamp_str_to_seconds(r["timestamp"]))
    upsampled_requests = [trace_json_data[0]] + upsampled_requests  # add header back

    # Save new JSON trace
    with open(dst_trace_file_path, "w") as f:
        json.dump(upsampled_requests, f, separators=(",", ":"))  # compact format

    print(f"Upsampled trace written to {dst_trace_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upsample trace by multiplexing requests")
    parser.add_argument("--trace_file_path", type=str, required=True, help="Path to input trace JSON file")
    parser.add_argument("--sweep_ratio", type=int, default=4, help="Number of times to upsample RPS (default=4)")
    args = parser.parse_args()

    main(args.trace_file_path, args.sweep_ratio)