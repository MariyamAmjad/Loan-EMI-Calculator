import csv
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt

filename = "results/r3_rate100_pod_metrics.csv"
pod_data = defaultdict(lambda: {"time": [], "cpu": []})

with open(filename, newline="") as f:
    for row in csv.DictReader(f):
        pod = row["pod"]

        if not pod.startswith("emi-web"):
            continue

        timestamp = datetime.fromisoformat(row["timestamp"])
        cpu = float(row["cpu"].replace("m", ""))

        pod_data[pod]["time"].append(timestamp)
        pod_data[pod]["cpu"].append(cpu)

plt.figure(figsize=(11, 6))

for pod, values in sorted(pod_data.items()):
    plt.plot(
        values["time"],
        values["cpu"],
        marker="o",
        linewidth=2,
        label=pod
    )

plt.title("Per-Pod CPU Utilization During 100 Requests/sec Test")
plt.xlabel("Time")
plt.ylabel("CPU Usage (millicores)")
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend(fontsize=8)
plt.xticks(rotation=30)
plt.tight_layout()

output = "results/graph2_pod_cpu.png"
plt.savefig(output, dpi=300)
print(f"Graph saved: {output}")
plt.close()

print(f"Web pods plotted: {len(pod_data)}")
for pod in sorted(pod_data):
    print(f"{pod}: {len(pod_data[pod]['cpu'])} samples")
