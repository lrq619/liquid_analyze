import os
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
def retrieve_run_interval(run_dir_path: str):
    log_path = os.path.join(run_dir_path, "loadgen.err")
    if not os.path.isfile(log_path):
        raise FileNotFoundError(f"{log_path} does not exist")

    target_line = None
    with open(log_path, "r") as f:
        for line in f:
            if "Finished preparing http requests" in line:
                target_line = line.strip()
                break

    if not target_line:
        raise ValueError("No line found containing 'Finished preparing http requests'")

    try:
        timestamp_str = target_line.split(" Finished preparing")[0]
        sg_timezone = ZoneInfo("Asia/Singapore")
        sg_time = datetime.strptime(timestamp_str, "%Y/%m/%d %H:%M:%S").replace(tzinfo=sg_timezone)
    except Exception as e:
        raise ValueError(f"Failed to parse timestamp from line: {target_line}") from e

    def sg_time_to_utc(sg_time):
        return sg_time.astimezone(ZoneInfo("UTC")).isoformat().replace("+00:00", "Z")

    start_time_utc = sg_time_to_utc(sg_time)
    finish_time_utc = sg_time_to_utc(sg_time + timedelta(hours=2))

    return start_time_utc, finish_time_utc

class RequestData:
    def __init__(self, json_data):
        response = json_data['response']['response']
        if response == None:
            self.error_msg = "No response!"
            return
        if "message" in response.keys():
            self.error_msg = response['message']
            return
        self.error_msg = ""
        usage = response['usage']
        self.prompt_tokens = usage['prompt_tokens']
        self.decode_tokens = usage['completion_tokens']
        if "prefill_metrics_list" in response:
            self.init_pd(response)
        else:
            self.init_default(response)
    
    def init_default(self, response):
        metrics = response['metrics_list'][0]
        self.arrival_time = metrics['arrival_time']
        self.ttft = metrics['first_token_time'] - self.arrival_time
        self.waiting_latency = 0
        self.decode_latency = metrics['finished_time'] - metrics['first_token_time']

    def init_pd(self, response):
        decode_metrics = response['metrics_list'][0]
        router_metrics = response['router_timestamps']
        prefill_metrics= response['prefill_metrics_list'][0]
        self.arrival_time = router_metrics['request_arrival']
        self.ttft = prefill_metrics['first_token_time'] - prefill_metrics['arrival_time']
        self.decode_latency = decode_metrics['finished_time'] - decode_metrics['first_token_time']
        e2e = router_metrics['decodeFinished'] - router_metrics['request_arrival']
        self.waiting_latency = e2e - self.ttft - self.decode_latency


    def to_dict(self):
        if self.error_msg != "":
            return {"error": self.error_msg}
        return {
            "prompt_tokens": self.prompt_tokens,
            "decode_tokens": self.decode_tokens,
            "arrival_ts": self.arrival_time,
            "ttft": self.ttft,
            "waiting_latency": self.waiting_latency,
            "decode_latency": self.decode_latency
        }


def fetch_data(params_list, url):
    data = {}
    for params in params_list:
        response = requests.get(url, params=params)
        response_json = response.json()
        for result in response_json.get("data", {}).get("result", []):
            gpu_uuid = result["metric"].get("gpuIDs", "unknown")
            hostname = result['metric'].get("hostname", "unknown")
            instance_uuid = f"{hostname}-{gpu_uuid}"
            # metric_name = result["metric"]["__name__"]
            metric_name: str = params["query"]
            if metric_name.startswith("router"):
                instance_uuid = "router"
            
            if instance_uuid not in data:
                data[instance_uuid] = {}
            
            if metric_name not in data[instance_uuid]:
                data[instance_uuid][metric_name] = [] 
            data[instance_uuid][metric_name] += result["values"]
    return data
    