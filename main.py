import json

from utils import retrieve_run_interval, RequestData, fetch_data
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

data = {"prom_data": prom_data}
loadgen_data = []
loadgen_result_file_path = "/data/loadgen_result.json"

with open(loadgen_result_file_path) as f:
    for line in f.readlines():
        json_data = json.loads(line)
        request_data = RequestData(json_data)
        loadgen_data.append(request_data.to_dict())
data['loadgen_data'] = loadgen_data
report_file_path = "/data/report.json"
with open(report_file_path, 'w+') as f:
    json.dump(data, f)
