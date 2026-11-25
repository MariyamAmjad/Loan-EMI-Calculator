import argparse
import csv
import subprocess
import time
import psutil
from datetime import datetime, timezone
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--label", required=True)
parser.add_argument("--duration", type=int, default=60)
args = parser.parse_args()

results = Path("results")
results.mkdir(exist_ok=True)

host_file = results / f"{args.label}_host_cpu.csv"
pod_file = results / f"{args.label}_pod_metrics.csv"

with host_file.open("w", newline="") as hf, pod_file.open("w", newline="") as pf:
    host_writer = csv.writer(hf)
    pod_writer = csv.writer(pf)

    host_writer.writerow(["timestamp", "host_cpu_percent"])
    pod_writer.writerow(["timestamp", "pod", "cpu", "memory"])

    start = time.monotonic()
    next_pod_sample = start

    print(f"Collecting host CPU and pod metrics for {args.duration} seconds...")

    while time.monotonic() - start < args.duration:
        timestamp = datetime.now(timezone.utc).isoformat()

        # One-second overall Ubuntu VM CPU measurement.
        cpu_percent = psutil.cpu_percent(interval=1)
        host_writer.writerow([timestamp, cpu_percent])
        hf.flush()

        now = time.monotonic()

        # Collect all EMI pod CPU and memory every 15 seconds.
        if now >= next_pod_sample:
            result = subprocess.run(
                ["kubectl", "top", "pods", "-n", "emi", "--no-headers"],
                capture_output=True,
                text=True,
                timeout=10
            )

            sample_time = datetime.now(timezone.utc).isoformat()

            if result.returncode == 0:
                for line in result.stdout.strip().splitlines():
                    parts = line.split()
                    if len(parts) >= 3:
                        pod_writer.writerow([
                            sample_time, parts[0], parts[1], parts[2]
                        ])
                pf.flush()
            else:
                print("Warning: kubectl top failed:", result.stderr.strip())

            next_pod_sample = now + 15

print("Profiling completed.")
print(f"Host CPU data: {host_file}")
print(f"Pod metrics: {pod_file}")
