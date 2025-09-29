# -----------------------------------------------------------------------------
# Author: Allen Glenn E. Castillo
# Date: September 29, 2025
# -----------------------------------------------------------------------------
# This script generates a Cumulative Distribution Function (CDF) plot of
# transaction latencies under two conditions: normal operation and DDoS attack.
# The data is loaded from a CSV file containing simulation results. The script
# filters the data based on the 'dos' column to separate normal and attack
# scenarios, computes the CDF for each, and visualizes the latency distributions.
# The resulting figure is saved for use in research documentation.
# -----------------------------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load simulation results from CSV file.
# The file is expected to contain columns including 'dos' (attack flag)
# and 'latency_ms_mean' (mean transaction latency in milliseconds).
df = pd.read_csv("results/sim_runs.csv")

# Filter data for normal operation (dos == 0) and DDoS attack (dos == 1).
normal_df = df[df["dos"] == 0]
ddos_df = df[df["dos"] == 1]


def get_latency_cdf(data):
    """
    Computes the Cumulative Distribution Function (CDF) for transaction latencies.

    Parameters:
        data (pd.DataFrame): DataFrame containing 'latency_ms_mean' column.

    Returns:
        latencies_sorted (np.ndarray): Sorted latency values.
        cdf (np.ndarray): Cumulative percentage values corresponding to latencies.
    """
    latencies = data["latency_ms_mean"].values
    latencies_sorted = np.sort(latencies)
    cdf = np.arange(1, len(latencies_sorted) + 1) / len(latencies_sorted) * 100
    return latencies_sorted, cdf


# Compute CDF data for both scenarios.
normal_lat, normal_cdf = get_latency_cdf(normal_df)
ddos_lat, ddos_cdf = get_latency_cdf(ddos_df)

# Plot the latency CDFs for comparison.
plt.figure(figsize=(8, 5))
plt.plot(normal_lat, normal_cdf, label="Normal Operation", marker="o")
plt.plot(ddos_lat, ddos_cdf, label="DoS Attack", marker="x")
plt.xlabel("Latency (ms)")
plt.ylabel("Cumulative Percentage of Transactions (%)")
plt.title("Latency Distribution (CDF)")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save the figure to the specified directory for inclusion in research outputs.
plt.savefig("results/figures", dpi=300)
# plt.show()  # Uncomment to display the plot interactively.
