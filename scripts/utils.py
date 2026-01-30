import os
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import List
import numpy as np
import re
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

def get_router_start_end_time(router_err_path: str):
    if not os.path.isfile(router_err_path):
        raise FileNotFoundError(f"{router_err_path} does not exist")

    # Regex to match timestamps like: 2025/07/26 23:31:02.484976
    timestamp_re = re.compile(r'^(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d{6})')

    start_time = None
    end_time = None

    with open(router_err_path, "r") as f:
        lines = f.readlines()

    # Get start_time: first line with timestamp
    for line in lines:
        match = timestamp_re.match(line)
        if match:
            start_time = datetime.strptime(match.group(1), "%Y/%m/%d %H:%M:%S.%f")
            break

    # Get end_time: last line with timestamp (search in reverse)
    for line in reversed(lines):
        match = timestamp_re.match(line)
        if match:
            end_time = datetime.strptime(match.group(1), "%Y/%m/%d %H:%M:%S.%f")
            break

    return start_time, end_time

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
        self.id = response['id']
        usage = response['usage']
        self.prompt_tokens = usage['prompt_tokens']
        self.decode_tokens = usage['completion_tokens']
        if "router_timestamps" in response.keys():
            self.init_pd(response)
        else:
            self.init_default(response)
    
    def init_default(self, response):
        metrics = response['metrics_list'][0]
        self.arrival_time = metrics['arrival_time']
        self.ttft = metrics['first_token_time'] - self.arrival_time
        self.waiting_latency = 0
        self.decode_latency = metrics['finished_time'] - metrics['first_token_time']
        self.queueing_latency = metrics['first_scheduled_time'] - self.arrival_time
        self.decode_ttft = -1
        self.prefill_e2e = -1
        self.pd_same_node = 1  # Default value if no router metrics are available

    def init_pd(self, response):
        prefill_metrics = response['prefill_metrics_list'][0]
        decode_metrics = response['metrics_list'][0]
        router_metrics = response['router_timestamps'] 

        self.arrival_time = router_metrics['request_arrival']
        self.ttft = prefill_metrics['first_token_time'] - prefill_metrics['arrival_time']
        self.decode_latency = decode_metrics['finished_time'] - decode_metrics['first_token_time']
        e2e = router_metrics['decodeFinished'] - router_metrics['request_arrival']
        self.decode_ttft = decode_metrics['first_token_time'] - decode_metrics['arrival_time']
        prefill_kv_ready_latency = 0
        if "prefill_kv_ready" in router_metrics:
            prefill_kv_ready_latency = router_metrics['prefill_kv_ready'] - router_metrics['prefillFinished']
        self.waiting_latency = prefill_kv_ready_latency + self.decode_ttft
        self.queueing_latency = prefill_metrics['first_scheduled_time'] - prefill_metrics['arrival_time']
        self.prefill_e2e = prefill_metrics['finished_time'] - prefill_metrics['arrival_time']
        self.pd_same_node = router_metrics.get('pd_same_node', 1)


    def to_dict(self):
        if self.error_msg != "":
            return {"error": self.error_msg}
        return {
            "id": self.id,
            "prompt_tokens": self.prompt_tokens,
            "decode_tokens": self.decode_tokens,
            "arrival_time": self.arrival_time,
            "ttft": self.ttft,
            "waiting_latency": self.waiting_latency,
            "decode_latency": self.decode_latency,
            "queueing_latency": self.queueing_latency,
            "decode_ttft": self.decode_ttft,
            "prefill_e2e": self.prefill_e2e,
            "pd_same_node": self.pd_same_node,
        }

    @staticmethod
    def init_from_dict(data: dict):
        obj = RequestData.__new__(RequestData)  # bypass __init__
        obj.error_msg = data.get("error_msg", "")
        obj.id = data.get("id", "")
        obj.prompt_tokens = data.get("prompt_tokens")
        obj.decode_tokens = data.get("decode_tokens")
        obj.arrival_time = data.get("arrival_time")
        obj.ttft = data.get("ttft")
        obj.waiting_latency = data.get("waiting_latency")
        obj.decode_latency = data.get("decode_latency")
        obj.queueing_latency = data.get("queueing_latency")
        obj.decode_ttft = data.get("decode_ttft")
        obj.prefill_e2e = data.get("prefill_e2e")
        obj.pd_same_node = data.get("pd_same_node")
        return obj

    def satisfy_SLO(self):
        if self.prompt_tokens < 256:
            ttft_SLO = 0.25
        elif self.prompt_tokens < 1024:
            ttft_SLO = 0.4
        else:
            ttft_SLO = 2
        tbt_SLO = 0.1

        ttft_attain = self.ttft <= ttft_SLO
        
        avg_tbt = (self.waiting_latency+self.decode_latency) / self.decode_tokens
        tbt_attain = avg_tbt <= tbt_SLO
        return ttft_attain, tbt_attain

    def satisfy_prefill_SLO(self):
        if self.prompt_tokens < 256:
            prefill_SLO = 0.25
        elif self.prompt_tokens < 1024:
            prefill_SLO = 0.4
        else:
            prefill_SLO = 2
        # prefill_SLO = 2
        return self.ttft <= prefill_SLO

    def satisfy_decode_SLO(self):
        tbt_SLO = 0.1
        avg_tbt = (self.waiting_latency+self.decode_latency) / self.decode_tokens
        tbt_attain = avg_tbt <= tbt_SLO
        return tbt_attain

def fetch_instance_data(params_list, url):
    data = {}
    for params in params_list:
        metric_name = params["query"]
        if metric_name.startswith("router"):
            continue  # Skip router metrics for now
        response = requests.get(url, params=params)
        response_json = response.json()
        for result in response_json.get("data", {}).get("result", []):
            instance_uuid = result["metric"].get("liquid_instance_uuid", "unknown")
            model = result['metric'].get("liquid_model", "unknown")
            gpu_uuid = result["metric"].get("gpuIDs", "unknown")
            hostname = result['metric'].get("hostname", "unknown")
            is_convert = result['metric'].get("is_convert", "unknown")
            
            if instance_uuid not in data:
                data[instance_uuid] = {}
            
            if metric_name not in data[instance_uuid]:
                data[instance_uuid][metric_name] = [] 
            data[instance_uuid][metric_name] += result["values"]
            data[instance_uuid]['metadata'] = {
                "model": model,
                "gpu_uuid": gpu_uuid,
                "hostname": hostname,
                "is_convert": is_convert,
            }
    return data

def fetch_data(params_list, url):
    data = {}
    for params in params_list:
        metric_name = params["query"]
        if metric_name.startswith("router"):
            continue  # Skip router metrics for now
        response = requests.get(url, params=params)
        response_json = response.json()
        for result in response_json.get("data", {}).get("result", []):
            gpu_uuid = result["metric"].get("gpuIDs", "unknown")
            hostname = result['metric'].get("hostname", "unknown")
            instance_uuid = f"{hostname}-{gpu_uuid}"
            
            if instance_uuid not in data:
                data[instance_uuid] = {}
            
            if metric_name not in data[instance_uuid]:
                data[instance_uuid][metric_name] = [] 
            data[instance_uuid][metric_name] += result["values"]

    data['router'] = {}  # Initialize router data
    for params in params_list:
        metric_name = params["query"]
        if metric_name.startswith("router"):
            response = requests.get(url, params=params)
            response_json = response.json()
            for result in response_json.get("data", {}).get("result", []):
                model_name = result["metric"].get("model", "unknown")

                if model_name not in data['router']:
                    data['router'][model_name] = {}

                # Check if requestType exists
                request_type = result["metric"].get("requestType")
                if request_type is not None:
                    # Nested by requestType
                    if metric_name not in data['router'][model_name]:
                        data['router'][model_name][metric_name] = {}
                    if request_type not in data['router'][model_name][metric_name]:
                        data['router'][model_name][metric_name][request_type] = []

                    data['router'][model_name][metric_name][request_type] += result["values"]
                else:
                    # Original structure
                    if metric_name not in data['router'][model_name]:
                        data['router'][model_name][metric_name] = []

                    data['router'][model_name][metric_name] += result["values"]


    return data

def get_goodput(requests: List[RequestData]) -> float:
    arrival_times = []
    finished_times = []
    satisfy_slo_count = 0
    for request in requests:
        if request.error_msg != "":
            continue
        arrival_times.append(request.arrival_time)
        finish_time = request.arrival_time + request.ttft + request.waiting_latency + request.decode_latency
        finished_times.append(finish_time)
        if request.satisfy_SLO():
            satisfy_slo_count += 1
    start_time = min(arrival_times)
    end_time = max(finished_times)
    goodput = satisfy_slo_count / (end_time - start_time)
    return goodput

def get_p_ttft(requests: List[RequestData], p) -> float:
    ttfts = []
    for request in requests:
        if request.error_msg != "":
            continue
        ttfts.append(request.ttft)
    return np.percentile(ttfts, p)

def get_p_tpot(requests: List[RequestData], p) -> float:
    tpots = []
    for request in requests:
        if request.error_msg != "":
            continue
        tpot = request.decode_latency / request.decode_tokens
        tpots.append(tpot)
    return np.percentile(tpots, p)
    
    