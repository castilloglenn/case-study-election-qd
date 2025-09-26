import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("results/sim_runs.csv")

# Filter for Normal Operation and DDoS Attack
normal_df = df[df["dos"] == 0]
ddos_df = df[df["dos"] == 1]


def get_latency_cdf(data):
    latencies = data["latency_ms_mean"].values
    latencies_sorted = np.sort(latencies)
    cdf = np.arange(1, len(latencies_sorted) + 1) / len(latencies_sorted) * 100
    return latencies_sorted, cdf


# Get CDF data
normal_lat, normal_cdf = get_latency_cdf(normal_df)
ddos_lat, ddos_cdf = get_latency_cdf(ddos_df)

# Plot
plt.figure(figsize=(8, 5))
plt.plot(normal_lat, normal_cdf, label="Normal Operation", marker="o")
plt.plot(ddos_lat, ddos_cdf, label="DoS Attack", marker="x")
plt.xlabel("Latency (ms)")
plt.ylabel("Cumulative Percentage of Transactions (%)")
plt.title("Latency Distribution (CDF)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("results/figures", dpi=300)
# plt.show()
