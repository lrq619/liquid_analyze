from analyze import analyze_data
import json
run_log_dir = "/mnt/network_drive/lrq/logs/logs_2025-06-16-09-57-47/run_0"
metrics_list = ["vllm:gpu_cache_usage_perc"]
report_file_path = analyze_data(run_log_dir, metrics_list)
with open(report_file_path, 'r') as f:
    report = json.load(f)
    print(report)
