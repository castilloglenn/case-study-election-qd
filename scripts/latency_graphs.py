import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from pathlib import Path

sns.set_theme(style="whitegrid")

INFILE = Path("results/validation_results.csv")
OUTDIR = Path("results/figures")
OUTDIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INFILE)

# -----------------------------
# Figure 1: Latency vs voters
# -----------------------------
plt.figure(figsize=(7, 4))
ax = sns.lineplot(
    data=df,
    x="n_total_votes",
    y="latency_avg_ms",
    hue="scenario",
    style="replication",
    markers=True,
    dashes=False,
)
ax.set_xlabel("Total voters (n)")
ax.set_ylabel("Average latency (ms)")
ax.set_title("Average latency vs. voters")
plt.tight_layout()
latency_path = OUTDIR / "latency_vs_voters.png"
plt.savefig(latency_path, dpi=150)
plt.close()

# Optional: If you want p95 “tail” shading, uncomment below.
# This shades the area between mean and p95 for each (scenario, replication) series.
# import numpy as np
# plt.figure(figsize=(7,4))
# ax = sns.lineplot(
#     data=df,
#     x="n_total_votes",
#     y="latency_avg_ms",
#     hue="scenario",
#     style="replication",
#     markers=True,
#     dashes=False
# )
# # Draw p95 bands
# for (sc, r), sub in df.sort_values("n_total_votes").groupby(["scenario","replication"]):
#     x = sub["n_total_votes"].values
#     mean_y = sub["latency_avg_ms"].values
#     p95_y = sub["latency_p95_ms"].values
#     plt.fill_between(x, mean_y, p95_y, alpha=0.12, step="pre", label=None)
# ax.set_xlabel("Total voters (n)")
# ax.set_ylabel("Average latency (ms)")
# ax.set_title("Average latency vs. voters (mean with p95 band)")
# plt.tight_layout()
# plt.savefig(OUTDIR / "latency_vs_voters_with_p95.png", dpi=150)
# plt.close()

# ---------------------------------------
# Figure 2: Success rate by scenario/rep
# ---------------------------------------
# Aggregate (it’s constant across n in your CSV, but this keeps it general)
agg = df.groupby(["scenario", "replication"], as_index=False)["success_rate"].mean()

plt.figure(figsize=(6, 4))
ax = sns.barplot(data=agg, x="scenario", y="success_rate", hue="replication")
ax.yaxis.set_major_formatter(PercentFormatter(1.0))
ax.set_ylim(0.0, 1.0)
ax.set_ylabel("Success rate")
ax.set_title("Success rate by scenario")
# Annotate bars with percentages
for p in ax.patches:
    height = p.get_height()
    ax.annotate(
        f"{height*100:.1f}%",
        (p.get_x() + p.get_width() / 2, height),
        ha="center",
        va="bottom",
        fontsize=9,
        xytext=(0, 3),
        textcoords="offset points",
    )
plt.tight_layout()
success_path = OUTDIR / "success_rate_by_scenario.png"
plt.savefig(success_path, dpi=150)
plt.close()

print(f"Wrote:\n - {latency_path}\n - {success_path}")
