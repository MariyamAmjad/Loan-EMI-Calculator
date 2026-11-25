import argparse
import csv
import json
import random
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--rate", type=int, required=True, help="Target requests per second")
parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
parser.add_argument("--label", required=True, help="Unique run label")
parser.add_argument("--url", default="http://emi.local/api/emi")
args = parser.parse_args()

if args.rate < 1 or args.duration < 1:
    raise SystemExit("Rate and duration must be positive.")

results_dir = Path("results")
results_dir.mkdir(exist_ok=True)

csv_path = results_dir / f"{args.label}.csv"
summary_path = results_dir / f"{args.label}_summary.json"

def send_request():
    # Generate new valid inputs for every individual request.
    principal = random.randint(100000, 1000000)
    annual_rate = random.randint(1, 20)
    months = random.randint(12, 60)

    payload = json.dumps({
        "P": principal,
        "rate": annual_rate,
        "n": months
    }).encode()

    request = urllib.request.Request(
        args.url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    started = time.perf_counter()
    timestamp = datetime.now(timezone.utc).isoformat()
    status = 0
    served_by = ""
    error = ""

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
            body = json.loads(response.read().decode())
            served_by = body.get("servedBy", "")
            if status < 200 or status >= 300:
                error = f"HTTP {status}"
    except urllib.error.HTTPError as exc:
        status = exc.code
        error = f"HTTP {exc.code}"
    except Exception as exc:
        error = str(exc)

    latency_ms = (time.perf_counter() - started) * 1000

    return {
        "timestamp": timestamp,
        "P": principal,
        "rate": annual_rate,
        "n": months,
        "status": status,
        "latency_ms": round(latency_ms, 3),
        "servedBy": served_by,
        "error": error
    }

total_requests = args.rate * args.duration
workers = min(300, max(32, args.rate * 2))

print(f"Target: {args.rate} requests/second")
print(f"Duration: {args.duration} seconds")
print(f"Scheduled requests: {total_requests}")
print(f"Worker threads: {workers}")
print(f"URL: {args.url}")
print("Starting test...")

start = time.perf_counter()
futures = []

with ThreadPoolExecutor(max_workers=workers) as executor:
    for i in range(total_requests):
        target_time = start + (i / args.rate)
        delay = target_time - time.perf_counter()
        if delay > 0:
            time.sleep(delay)
        futures.append(executor.submit(send_request))

    rows = []
    for future in as_completed(futures):
        rows.append(future.result())

elapsed = time.perf_counter() - start
rows.sort(key=lambda row: row["timestamp"])

with csv_path.open("w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=[
        "timestamp", "P", "rate", "n", "status",
        "latency_ms", "servedBy", "error"
    ])
    writer.writeheader()
    writer.writerows(rows)

successful = [r for r in rows if 200 <= r["status"] < 300 and not r["error"]]
errors = len(rows) - len(successful)
average_latency = (
    sum(r["latency_ms"] for r in rows) / len(rows) if rows else 0
)

summary = {
    "label": args.label,
    "target_requests_per_second": args.rate,
    "duration_seconds": args.duration,
    "scheduled_requests": total_requests,
    "completed_requests": len(rows),
    "successful_requests": len(successful),
    "error_count": errors,
    "average_response_time_ms": round(average_latency, 3),
    "elapsed_seconds_including_completion": round(elapsed, 3),
    "completed_requests_per_second": round(len(rows) / elapsed, 3),
    "csv_file": str(csv_path)
}

with summary_path.open("w") as file:
    json.dump(summary, file, indent=4)

print("\n===== TEST SUMMARY =====")
print(json.dumps(summary, indent=4))
print(f"\nRaw request results: {csv_path}")
print(f"Summary: {summary_path}")
