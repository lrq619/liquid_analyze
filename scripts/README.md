We use a docker image to analyze the experiment data, it's in `lrq619/analyze`, you can either download it, or build it with
```
docker build -f Dockerfile.analyze .
```
Then, change the `run_log_dir` in the start of `analyze.ipynb` into the experiment data you want to analyze, for example:
```
run_log_dir = "/mnt/network_drive/lrq/logs/logs_2025-09-24-20-50-38/run_0"
```

Notice that each experiment might contain one or multiple `runs`(run_0, run_1, ...), these run folders are the analysis target.