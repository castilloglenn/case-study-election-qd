import pandas as pd
from pathlib import Path

df = pd.read_csv("results/sim_runs.csv")

# Filter for relevant scenarios
keep = df[
    (df.voters.isin([5000, 10000]))
    & (df.failure_rate == 0.10)
    & (df.base_latency_ms == 25)
]

# Add scenario label
keep["Scenario"] = keep.apply(lambda r: "DoS" if r.dos == 1 else "Normal", axis=1)

# Select and rename columns, including new ones from sweep.py
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

out.to_csv("results/table_core.csv", index=False)
print(out.to_markdown(index=False))
