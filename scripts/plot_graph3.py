import csv
import math
import matplotlib.pyplot as plt

filename = "results/autoscaling_metrics.csv"

times = []
rates = []
cpu_values = []
current_replicas = []
desired_replicas = []

with open(filename, newline="") as f:
    for row in csv.DictReader(f):
        times.append(float(row["elapsed_seconds"]) / 60)
        rates.append(float(row["request_rate"]))

        cpu = row["average_cpu_utilization_percent"]
        cpu_values.append(float(cpu) if cpu else math.nan)

        current_replicas.append(
            int(row["current_replicas"])
            if row["current_replicas"] else math.nan
        )
        desired_replicas.append(
            int(row["desired_replicas"])
            if row["desired_replicas"] else math.nan
        )

fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

# Plot 1: Request rate
axes[0].step(times, rates, where="post", marker="o")
axes[0].set_ylabel("Requests/sec")
axes[0].set_title("Autoscaling Test: Request Rate, CPU and Replicas")
axes[0].grid(True, linestyle="--", alpha=0.5)

# Plot 2: Average CPU utilization
axes[1].plot(times, cpu_values, marker="o", linewidth=2)
axes[1].axhline(50, linestyle="--", label="HPA target: 50%")
axes[1].set_ylabel("Average CPU (%)")
axes[1].legend()
axes[1].grid(True, linestyle="--", alpha=0.5)

# Plot 3: Current and desired replicas
axes[2].step(
    times, current_replicas,
    where="post", marker="o", label="Current replicas"
)
axes[2].step(
    times, desired_replicas,
    where="post", marker="x", linestyle="--",
    label="Desired replicas"
)
axes[2].set_ylabel("Replica count")
axes[2].set_xlabel("Elapsed time (minutes)")
axes[2].set_yticks(range(1, 6))
axes[2].set_ylim(0.5, 5.5)
axes[2].legend()
axes[2].grid(True, linestyle="--", alpha=0.5)

for ax in axes:
    ax.axvline(2, color="gray", linestyle=":", alpha=0.7)
    ax.axvline(7, color="gray", linestyle=":", alpha=0.7)

axes[2].set_xlim(left=0)
plt.tight_layout()

output = "results/graph3_autoscaling.png"
plt.savefig(output, dpi=300)
plt.close()

print(f"Graph saved: {output}")
print(f"Recorded samples: {len(times)}")
print(f"Samples with CPU readings: {sum(not math.isnan(v) for v in cpu_values)}")
print(f"Maximum current replicas: {max(v for v in current_replicas if not math.isnan(v))}")
