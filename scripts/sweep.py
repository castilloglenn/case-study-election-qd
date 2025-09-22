import asyncio, csv, time, statistics, random
from pathlib import Path
from network_simulation import simulate
import itertools

OUT = Path("results/sim_runs.csv")
OUT.parent.mkdir(exist_ok=True, parents=True)


def ci95(xs):
    if len(xs) < 2:
        return (0.0, 0.0)
    m = statistics.mean(xs)
    s = statistics.stdev(xs)
    half = 1.96 * s / (len(xs) ** 0.5)
    return (m, half)


async def one_cell(voters, failure_rate, base_lat_ms, dos, repl_factor, reps=10):
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
        latencies.append(avg_lat * 1000.0)  # s -> ms
        throughputs.append(thr)
        success.append(succ)
        tamper.append(tamper_rate)
    return latencies, throughputs, success, tamper


async def main():
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

        # Run all parameter combinations concurrently for faster execution

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
            async with semaphore:
                return await run_and_write(params)

        results = await asyncio.gather(*(sem_run(params) for params in param_grid))
        for row in results:
            w.writerow(row)


if __name__ == "__main__":
    asyncio.run(main())
