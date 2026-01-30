from analyze import analyze_data
import json
run_log_dir = "/mnt/network_drive/lrq/logs/logs_2025-06-19-15-39-05/run_0"
metrics_list = ["vllm:gpu_cache_usage_perc"]
report_file_path = analyze_data(run_log_dir, metrics_list)
with open(report_file_path, 'r') as f:
    report = json.load(f)

loadgen_data = report['loadgen_data']
total_request_count = len(loadgen_data)
no_response_count = 0
error_count = 0
for request_data in loadgen_data:
    if 'error' not in request_data.keys():
        continue

    if request_data == {'error': 'No response!'}:
        no_response_count += 1
    else:
        error_count += 1
        print(request_data['error'])

print(f"Total request: {total_request_count}, no response: {no_response_count}, error: {error_count}")
recv_kv_failed_requests = report['recv_failed_requests']
print(f"There are totally {len(recv_kv_failed_requests)} requests fall back to model forwarding!")
print()


