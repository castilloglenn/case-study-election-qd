# Author: Allen Glenn E. Castillo
# Date: September 29, 2025
#
# This script processes simulation results for a case study on election system reliability.
# It reads experiment data from 'results/sim_runs.csv', filters for scenarios with specific voter counts,
# failure rates, and base latency settings, and labels each scenario as either 'DoS' or 'Normal' based on
# the presence of denial-of-service conditions. The script then selects relevant metrics, including those
# added in 'sweep.py', rounds numerical values for clarity, and renames columns for presentation.
# The processed table is saved to 'results/table_core.csv' and printed in markdown format for inclusion
# in research documentation. This workflow supports reproducible analysis and reporting of core experimental
# outcomes in the election system study.

import pandas as pd
from pathlib import Path

df = pd.read_csv("results/sim_runs.csv")

# Filter for relevant scenarios: voter counts of 5000 or 10000, failure rate of 0.10, and base latency of 25ms
keep = df[
    (df.voters.isin([5000, 10000]))
    & (df.failure_rate == 0.10)
    & (df.base_latency_ms == 25)
]

# Add scenario label: 'DoS' if denial-of-service is present, otherwise 'Normal'
keep["Scenario"] = keep.apply(lambda r: "DoS" if r.dos == 1 else "Normal", axis=1)

# Select and rename columns for reporting, including metrics from sweep.py
cols = [
    "Scenario",
    "voters",
    "failure_rate",
    "base_latency_ms",
    "replication_factor",
    "latency_ms_mean",
    "latency_ms_ci95",
    "throughput_mean",
    "throughput_ci95",
    "success_pct_mean",
    "success_pct_ci95",
    "tamper_pct_mean",
    "tamper_pct_ci95",
]

out = (
    keep[cols]
    .round(2)
    .rename(
        columns={
            "voters": "Voters",
            "failure_rate": "Fail Rate",
            "base_latency_ms": "Base Lat (ms)",
            "replication_factor": "Repl",
            "latency_ms_mean": "Latency (ms)",
            "latency_ms_ci95": "Latency CI95",
            "throughput_mean": "Throughput (v/s)",
            "throughput_ci95": "Throughput CI95",
            "success_pct_mean": "Success (%)",
            "success_pct_ci95": "Success CI95",
            "tamper_pct_mean": "Tamper (%)",
            "tamper_pct_ci95": "Tamper CI95",
        }
    )
)

# Save the processed table for research documentation and print as markdown
out.to_csv("results/table_core.csv", index=False)
print(out.to_markdown(index=False))
