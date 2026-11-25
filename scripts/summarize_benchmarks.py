import csv
import json
import re
from pathlib import Path

results_dir = Path("results")
rows = []

for file in results_dir.glob("r[123]_rate*_summary.json"):
    match = re.fullmatch(r"r([123])_rate(\d+)_summary", file.stem)
    if not match:
        continue

    replicas = int(match.group(1))
    rate = int(match.group(2))

    with file.open() as f:
        data = json.load(f)

    rows.append({
        "replicas": replicas,
        "target_requests_per_second": rate,
        "scheduled_requests": data["scheduled_requests"],
        "completed_requests": data["completed_requests"],
        "successful_requests": data["successful_requests"],
        "error_count": data["error_count"],
        "average_response_time_ms": data["average_response_time_ms"],
        "actual_throughput_rps": data["completed_requests_per_second"],
    })

rows.sort(key=lambda x: (x["replicas"], x["target_requests_per_second"]))

output = results_dir / "fixed_replica_summary.csv"

with output.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Total benchmark runs: {len(rows)}")
print(f"Saved: {output}")
print()
print(f"{'Replicas':<10} {'Rate':<8} {'Success':<10} {'Errors':<8} {'Avg response (ms)':<20} {'Actual RPS'}")
print("-" * 75)

for r in rows:
    print(
        f"{r['replicas']:<10} "
        f"{r['target_requests_per_second']:<8} "
        f"{r['successful_requests']:<10} "
        f"{r['error_count']:<8} "
        f"{r['average_response_time_ms']:<20.3f} "
        f"{r['actual_throughput_rps']:.3f}"
    )
