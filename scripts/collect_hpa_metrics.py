import csv
import json
import subprocess
import time
from datetime import datetime, timezone
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--duration", type=int, default=610)
parser.add_argument("--interval", type=int, default=15)
parser.add_argument("--output", default="results/autoscaling_metrics.csv")
args = parser.parse_args()

start = time.monotonic()
end = start + args.duration

with open(args.output, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "timestamp",
        "elapsed_seconds",
        "phase",
        "request_rate",
        "average_cpu_utilization_percent",
        "average_cpu_millicores",
        "current_replicas",
        "desired_replicas"
    ])

    sample = 0

    while time.monotonic() < end:
        elapsed = round(time.monotonic() - start)

        if elapsed < 120:
            phase, rate = "initial_low", 10
        elif elapsed < 420:
            phase, rate = "high_load", 100
        else:
            phase, rate = "final_low", 10

        try:
            result = subprocess.run(
                ["kubectl", "get", "hpa", "emi-web", "-n", "emi", "-o", "json"],
                capture_output=True, text=True, check=True, timeout=10
            )
            hpa = json.loads(result.stdout)
            status = hpa.get("status", {})

            current_replicas = status.get("currentReplicas", "")
            desired_replicas = status.get("desiredReplicas", "")

            cpu_percent = ""
            cpu_millicores = ""

            for metric in status.get("currentMetrics", []):
                if metric.get("type") == "Resource":
                    resource = metric.get("resource", {})
                    if resource.get("name") == "cpu":
                        current = resource.get("current", {})
                        cpu_percent = current.get("averageUtilization", "")
                        cpu_millicores = current.get("averageValue", "")

            writer.writerow([
                datetime.now(timezone.utc).isoformat(),
                elapsed,
                phase,
                rate,
                cpu_percent,
                cpu_millicores,
                current_replicas,
                desired_replicas
            ])
            f.flush()

            sample += 1
            print(
                f"Sample {sample}: {elapsed}s | {phase} | "
                f"CPU {cpu_percent}% | "
                f"replicas {current_replicas}/{desired_replicas}"
            )

        except Exception as e:
            print(f"Sample error at {elapsed}s: {e}")

        remaining = end - time.monotonic()
        if remaining > 0:
            time.sleep(min(args.interval, remaining))

print(f"Metrics saved: {args.output}")
print(f"Total samples: {sample}")
