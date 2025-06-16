import os
import json
import subprocess
IMAGE_NAME = "lrq619/analyze:latest"

def analyze_data(run_log_dir, metrics_list):
    query_file_path = os.path.join(run_log_dir, "query.json")
    with open(query_file_path, "w+") as f:
        json.dump(metrics_list, f)
        
    cmd = f"docker run -v {run_log_dir}:/data {IMAGE_NAME}"
    subprocess.run(cmd, shell=True, check=True)

    report_file_path = os.path.join(run_log_dir, "report.json")
    assert os.path.exists(report_file_path)
    return report_file_path
    