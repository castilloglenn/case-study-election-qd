import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

IN = Path("results/sim_runs.csv")
OUT = Path("results/figures")
OUT.mkdir(exist_ok=True, parents=True)

df = pd.read_csv(IN)

# 1) Latency vs Voters (separate lines for dos 0/1; optionally separate panels for repl_factor)
for repl in sorted(df.replication_factor.unique()):
    sub = df[
        (df.replication_factor == repl)
        & (df.failure_rate == 0.10)
        & (df.base_latency_ms == 25)
    ]
    pivot = sub.pivot_table(index="voters", columns="dos", values="latency_ms_mean")
    err = sub.pivot_table(index="voters", columns="dos", values="latency_ms_ci95")
    ax = pivot.plot(yerr=err, marker="o", linewidth=1.5)
    ax.set_xlabel("Voters (count)")
    ax.set_ylabel("Average Latency (ms)")
    ax.set_title(
        f"Latency vs. Voters (replication={repl}, failure_rate=10%, base=25ms)"
    )
    ax.grid(True, linestyle=":")
    plt.tight_layout()
    plt.savefig(OUT / f"latency_vs_voters_repl{repl}.png", dpi=300)
    plt.clf()
    plt.close()

# 2) Throughput vs Replication (bars, under DoS on)
sub = df[
    (df.dos == 1)
    & (df.voters == 10_000)
    & (df.base_latency_ms == 25)
    & (df.failure_rate == 0.10)
]
ax = sub.plot(
    x="replication_factor",
    y="throughput_mean",
    kind="bar",
    yerr=sub["throughput_ci95"].values,
    legend=False,
)
ax.set_xlabel("Replication Factor")
ax.set_ylabel("Throughput (votes/s)")
ax.set_title("Throughput under DoS (10k voters, base=25ms, fail=10%)")
ax.grid(axis="y", linestyle=":")
plt.tight_layout()
plt.savefig(OUT / "throughput_vs_replication_dos.png", dpi=300)
plt.clf()
plt.close()

# 3) Success Rate Heatmap (voters × replication) under DoS
sub = df[(df.dos == 1) & (df.base_latency_ms == 25) & (df.failure_rate == 0.10)]
pivot = sub.pivot_table(
    index="voters", columns="replication_factor", values="success_pct_mean"
)
fig, ax = plt.subplots()
im = ax.imshow(pivot.values, aspect="auto", cmap="viridis")
ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(pivot.columns)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index)
ax.set_xlabel("Replication Factor")
ax.set_ylabel("Voters")
ax.set_title("Success Rate (%) under DoS")
for i in range(pivot.shape[0]):
    for j in range(pivot.shape[1]):
        ax.text(
            j, i, f"{pivot.values[i,j]:.1f}", ha="center", va="center", color="white"
        )
plt.colorbar(im, ax=ax, label="Success Rate (%)")
plt.tight_layout()
plt.savefig(OUT / "success_heatmap.png", dpi=300)
plt.clf()
plt.close()
