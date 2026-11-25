import csv
import matplotlib.pyplot as plt

data = {}

with open("results/fixed_replica_summary.csv", newline="") as f:
    for row in csv.DictReader(f):
        replicas = int(row["replicas"])
        data.setdefault(replicas, []).append(row)

plt.figure(figsize=(10, 6))

for replicas in sorted(data):
    rows = sorted(
        data[replicas],
        key=lambda x: int(x["target_requests_per_second"])
    )
    rates = [int(r["target_requests_per_second"]) for r in rows]
    times = [float(r["average_response_time_ms"]) for r in rows]

    plt.plot(rates, times, marker="o", linewidth=2,
             markersize=7, label=f"{replicas} replica(s)")

plt.title("Average Response Time vs Request Rate")
plt.xlabel("Target Request Rate (requests/second)")
plt.ylabel("Average Response Time (ms)")
plt.xticks([10, 25, 50, 100, 200])
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()
plt.tight_layout()

output = "results/graph1_response_time.png"
plt.savefig(output, dpi=300)
print(f"Graph saved: {output}")
plt.show()
