# -----------------------------------------------------------------------------
# Title: Parameter Sweep for Network Simulation
# Author: Allen Glenn E. Castillo
# Date: September 29, 2025
#
# Description:
# This script performs a comprehensive parameter sweep for a network simulation
# study, evaluating the effects of various system configurations on performance
# and reliability metrics. The simulation investigates the impact of voter count,
# node failure rate, base network latency, denial-of-service (DoS) attacks, and
# replication factor on distributed voting system outcomes.
#
# Methodology:
# - The script generates all combinations of specified parameters.
# - For each combination, it runs multiple simulation replicates to collect
#   latency, throughput, success rate, and tamper rate metrics.
# - Results are aggregated and summarized using mean and 95% confidence intervals.
# - All results are written to a CSV file for further analysis.
#
# Usage:
# Run this script to produce a CSV file containing summarized results for each
# parameter combination. The simulation logic is provided by the `simulate`
# function in the `network_simulation` module.
#
# Output:
# - results/sim_runs.csv: Contains one row per parameter combination, including
#   summary statistics for each measured metric.
#
# -----------------------------------------------------------------------------

import asyncio, csv, time, statistics, random
from pathlib import Path
from network_simulation import simulate
import itertools

OUT = Path("results/sim_runs.csv")
OUT.parent.mkdir(exist_ok=True, parents=True)


def ci95(xs):
    """
    Compute mean and 95% confidence interval for a list of values.
    Returns (mean, half-width of CI).
    """
    if len(xs) < 2:
        return (0.0, 0.0)
    m = statistics.mean(xs)
    s = statistics.stdev(xs)
    half = 1.96 * s / (len(xs) ** 0.5)
    return (m, half)


async def one_cell(voters, failure_rate, base_lat_ms, dos, repl_factor, reps=10):
    """
    Run multiple replicates of the simulation for a given parameter set.
    Returns lists of latency, throughput, success rate, and tamper rate.
    """
    latencies, throughputs, success, tamper = [], [], [], []
    for _ in range(reps):
        avg_lat, thr, succ, tamper_rate = await simulate(
            votes=voters,
            dos_attack=dos,
            failure_rate=failure_rate,
            base_latency_ms=base_lat_ms,
            replication_factor=repl_factor,
            jitter=True,
        )
        latencies.append(avg_lat * 1000.0)  # Convert seconds to milliseconds
        throughputs.append(thr)
        success.append(succ)
        tamper.append(tamper_rate)
    return latencies, throughputs, success, tamper


async def main():
    """
    Main entry point: runs the parameter sweep and writes results to CSV.
    """
    fieldnames = [
        "voters",
        "failure_rate",
        "base_latency_ms",
        "dos",
        "replication_factor",
        "replicates",
        "latency_ms_mean",
        "latency_ms_ci95",
        "throughput_mean",
        "throughput_ci95",
        "success_pct_mean",
        "success_pct_ci95",
        "tamper_pct_mean",
        "tamper_pct_ci95",
    ]
    write_header = not OUT.exists()
    with OUT.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            w.writeheader()

        # Generate all parameter combinations
        param_grid = list(
            itertools.product(
                [1_000, 5_000, 10_000],  # voters
                [0.0, 0.10],  # failure_rate
                [5, 25],  # base_lat_ms
                [False, True],  # dos
                [1, 3],  # repl_factor
            )
        )

        async def run_and_write(params):
            """
            Run simulation for a parameter set and format results for CSV.
            """
            voters, failure_rate, base_lat_ms, dos, repl_factor = params
            lats, thrs, succs, tampers = await one_cell(
                voters,
                failure_rate,
                base_lat_ms,
                dos,
                repl_factor,
                reps=10,
            )
            lm, lci = ci95(lats)
            tm, tci = ci95(thrs)
            sm, sci = ci95(succs)
            tpm, tpci = ci95(tampers)
            return {
                "voters": voters,
                "failure_rate": failure_rate,
                "base_latency_ms": base_lat_ms,
                "dos": int(dos),
                "replication_factor": repl_factor,
                "replicates": len(lats),
                "latency_ms_mean": round(lm, 3),
                "latency_ms_ci95": round(lci, 3),
                "throughput_mean": round(tm, 3),
                "throughput_ci95": round(tci, 3),
                "success_pct_mean": round(sm, 3),
                "success_pct_ci95": round(sci, 3),
                "tamper_pct_mean": round(tpm, 3),
                "tamper_pct_ci95": round(tpci, 3),
            }

        # Limit concurrency to avoid overwhelming the system
        semaphore = asyncio.Semaphore(8)

        async def sem_run(params):
            """
            Wrapper to run simulations with concurrency control.
            """
            async with semaphore:
                return await run_and_write(params)

        # Run all simulations concurrently
        results = await asyncio.gather(*(sem_run(params) for params in param_grid))
        for row in results:
            w.writerow(row)


if __name__ == "__main__":
    asyncio.run(main())
