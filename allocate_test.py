import os
import time
import torch
import gc
import subprocess
import multiprocessing
import traceback


def preallocate_pinned_cpu_buffer():
    # Get buffer size from environment
    buf_gb_str = os.environ.get("NIXL_RECEIVER_BUFFER_SIZE_GB")
    if buf_gb_str is None:
        raise ValueError("Environment variable NIXL_RECEIVER_BUFFER_SIZE_GB not set.")
    try:
        buf_gb = float(buf_gb_str)
    except ValueError:
        raise ValueError(f"Invalid value for NIXL_RECEIVER_BUFFER_SIZE_GB: {buf_gb_str}")

    # Get GPU count using subprocess (no CUDA init)
    out = subprocess.check_output(["nvidia-smi", "--list-gpus"]).decode()
    gpu_count = len([line for line in out.splitlines() if line.strip()])
    if gpu_count == 0:
        raise RuntimeError("No GPU detected.")
    print(f"[Parent] Detected {gpu_count} GPUs.")

    # Compute total buffer size
    total_gb = buf_gb * gpu_count
    total_bytes = int(total_gb * (1024 ** 3))
    num_elems = total_bytes // torch.tensor([], dtype=torch.uint8, device="cpu").element_size()
    print(f"[Parent] Allocating {total_gb:.2f} GB pinned CPU tensor...")

    t0 = time.perf_counter()
    buf = torch.empty(num_elems, dtype=torch.uint8, device="cpu")
    # del buf
    gc.collect()
    t1 = time.perf_counter()

    print(f"[Parent] Total time (alloc + free): {t1 - t0:.3f} seconds")
    return total_gb


def child_process(total_gb):
    print(f"[Child] Starting CUDA initialization test...")

    # Try to initialize CUDA
    t0 = time.perf_counter()
    torch.cuda.init()
    gpu_count = torch.cuda.device_count()

    # Allocate CPU pinned buffer of same size
    total_bytes = int(total_gb * (1024 ** 3))
    num_elems = total_bytes // torch.tensor([], dtype=torch.uint8).element_size()
    print(f"[Child] Allocating {total_gb:.2f} GB pinned CPU tensor...")

    torch.cuda.synchronize()
    t1 = time.perf_counter()
    print(f"[Child] init cuda takes {t1 - t0:.3f} seconds, detected {gpu_count} GPUs.")
    buf = torch.empty(num_elems, dtype=torch.uint8, device="cpu", pin_memory=True)
    del buf
    gc.collect()
    t2 = time.perf_counter()

    print(f"[Child] CPU pinned tensor allocation time: {t2 - t1:.3f} seconds")


if __name__ == "__main__":
    # Step 1: run preallocation in parent
    total_gb = preallocate_pinned_cpu_buffer()

    # Step 2: fork child process (no CUDA context inherited)
    print("\n[Fork] Spawning child process...\n")
    proc = multiprocessing.Process(target=child_process, args=(total_gb,))
    proc.start()
    proc.join()

    print("\n✅ Test complete.")