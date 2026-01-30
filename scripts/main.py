import json
import re
import os

from utils import retrieve_run_interval, RequestData, fetch_data, fetch_instance_data, get_router_start_end_time
query_metric_file = "/data/query.json"
start_time, end_time = retrieve_run_interval("/data")

query_metric_list = []
with open(query_metric_file, 'r') as f:
    query_metric_list = json.load(f)

print(f"query_metrics_list: {query_metric_list}")


params_list = []
for query_metric in query_metric_list:
    params_list.append(
        {"query": query_metric, "start": start_time, "end": end_time, "step": "1s"}
    )
url = "http://localhost:9090/api/v1/query_range"
# Fetch data for both metrics
print(f"params_list: {params_list}")
prom_data = fetch_data(params_list, url)
prom_instance_data = fetch_instance_data(params_list, url)

data = {
    "prom_data": prom_data
    , "prom_instance_data": prom_instance_data
}
loadgen_data = []
loadgen_result_file_path = "/data/loadgen_result.json"

with open(loadgen_result_file_path) as f:
    for line in f.readlines():
        try:
            json_data = json.loads(line)
        except:
            print(line)
        request_data = RequestData(json_data)
        loadgen_data.append(request_data.to_dict())
data['loadgen_data'] = loadgen_data

recv_kv_failed_requests = []

# Pattern to match filenames
filename_pattern = re.compile(r"^worker_.*\.out$")

# Pattern to match the log line and extract the request ID
# line_pattern = re.compile(
#     r"\[KV-transfer\] request recv kv failed!:\s+(cmpl-[a-f0-9\-]+)"
# )
# log_dir = "/data"
# # Walk through files in the directory
# for filename in os.listdir(log_dir):
#     if filename_pattern.match(filename):
#         full_path = os.path.join(log_dir, filename)
#         with open(full_path, "r") as file:
#             for line in file:
#                 match = line_pattern.search(line)
#                 if match:
#                     request_id = match.group(1)
#                     recv_kv_failed_requests.append(request_id)
# data['recv_failed_requests'] = recv_kv_failed_requests
data['recv_failed_requests'] = []
router_start_time, router_end_time = get_router_start_end_time("/data/router.err")
data['router_start_time'] = router_start_time.isoformat()
data['router_end_time'] = router_end_time.isoformat()


report_file_path = "/data/report.json"
with open(report_file_path, 'w+') as f:
    json.dump(data, f)
