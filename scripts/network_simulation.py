# ============================================================
# Title: Network Simulation for Election Case Study
# Author: Allen Glenn E. Castillo
# Date: September 29, 2025
# ============================================================
#
# This script simulates a network of nodes processing votes in an election scenario.
# It models network latency, node failures, jitter, burst packet drops, and Byzantine faults.
# The simulation is designed to analyze the reliability, latency, throughput, and tamper detection
# in a distributed system under various adverse conditions.
#
# Classes:
#   - Node: Represents a generic network node with configurable failure rate, latency, and jitter.
#   - Head: Inherits from Node; simulates a Byzantine node that may tamper with data.
#   - Capital: Inherits from Node; collects received votes and detects tampering.
#
# Main Simulation Function:
#   - simulate: Runs the voting process through the network, applying configured attack/fault scenarios.
#     Parameters allow control over vote count, DoS attacks, burst drops, replication, and Byzantine probability.
#     Collects statistics on latency, throughput, success rate, and tamper detection.
#
# Usage:
#   - The script can be run directly. The main() function demonstrates several scenarios:
#       * Normal operation
#       * DoS attack simulation
#       * Burst packet drop simulation
#       * Byzantine node simulation with replication
#
# Research Context:
#   - This simulation is intended for research on secure and reliable distributed voting systems.
#   - Results can be used to evaluate system robustness against network faults and adversarial behaviors.
#
# ============================================================

import asyncio
import random
import time
import statistics


class Node:
    """
    Represents a network node in the simulation.

    Attributes:
        name (str): Identifier for the node.
        failure_rate (float): Probability of message loss.
        latency (float): Base network latency in seconds.
        jitter (bool): If True, adds random jitter to latency.
    """

    def __init__(self, name, failure_rate=0.0, latency=0.01, jitter=False):
        self.name = name
        self.failure_rate = failure_rate
        self.latency = latency
        self.jitter = jitter

    async def send(self, data, next_node):
        """
        Simulates sending data to the next node with latency, jitter, and possible failure.

        Args:
            data: Data to send.
            next_node: Node to receive the data.

        Returns:
            Result from next_node.receive(data) or None if failed.
        """
        lat = self.latency
        if self.jitter:
            lat += random.uniform(0, self.latency)
        await asyncio.sleep(lat)
        if random.random() < self.failure_rate:
            return None
        return await next_node.receive(data)

    async def receive(self, data):
        """
        Simulates receiving data with latency and jitter.

        Args:
            data: Data received.

        Returns:
            The received data.
        """
        lat = self.latency
        if self.jitter:
            lat += random.uniform(0, self.latency)
        await asyncio.sleep(lat)
        return data


class Head(Node):
    """
    Special node that may act as a Byzantine adversary, tampering with data.

    Attributes:
        byzantine_prob (float): Probability of tampering with received data.
    """

    def __init__(self, name, latency=0.01, byzantine_prob=0.0, jitter=False):
        super().__init__(name, latency=latency, jitter=jitter)
        self.byzantine_prob = byzantine_prob

    async def receive(self, data):
        """
        Receives data and may tamper with it based on byzantine_prob.

        Args:
            data: Data received.

        Returns:
            Tampered or original data.
        """
        if self.byzantine_prob > 0 and random.random() < self.byzantine_prob:
            data = f"{data}-tampered"
        return await super().receive(data)


class Capital(Node):
    """
    Final node that collects votes and detects tampering.

    Attributes:
        received (list): List of successfully received votes and timestamps.
        tampered (int): Count of tampered votes detected.
    """

    def __init__(self, name):
        super().__init__(name)
        self.received = []
        self.tampered = 0

    async def receive(self, data):
        """
        Receives data, checks for tampering, and records successful votes.

        Args:
            data: Data received.

        Returns:
            True if vote is valid, False if tampered.
        """
        if "tampered" in data:
            self.tampered += 1
            return False
        self.received.append((data, time.time()))
        return True


async def simulate(
    votes=1000,
    dos_attack=False,
    failure_rate=0.0,
    base_latency_ms=5,
    replication_factor=1,
    jitter=False,
    burst_drop=False,
    burst_len=50,
    p_burst=0.5,
    byzantine_prob=0.0,
):
    """
    Runs the network simulation for a given number of votes and attack/fault parameters.

    Args:
        votes (int): Number of votes to simulate.
        dos_attack (bool): If True, simulates DoS attack conditions.
        failure_rate (float): Base failure rate for nodes.
        base_latency_ms (float): Base latency in milliseconds.
        replication_factor (int): Number of times each vote is sent (for redundancy).
        jitter (bool): If True, enables latency jitter.
        burst_drop (bool): If True, simulates burst packet drops.
        burst_len (int): Length of burst drop period.
        p_burst (float): Failure rate during burst.
        byzantine_prob (float): Probability of Byzantine tampering at Head node.

    Returns:
        avg_latency (float): Average latency of successful votes.
        throughput (float): Votes processed per second.
        success_rate (float): Percentage of successful votes.
        tamper_rate (float): Percentage of tampered votes detected.
    """
    base_latency = base_latency_ms / 1000.0
    node = Node("Node", failure_rate=failure_rate, latency=base_latency, jitter=jitter)
    head = Head(
        "Head", latency=base_latency * 2, byzantine_prob=byzantine_prob, jitter=jitter
    )
    capital = Capital("Capital")

    latencies = []
    tampered_detected = 0
    start_time = time.time()

    burst_active = False
    burst_counter = 0

    for i in range(votes):
        vote = f"vote-{i}"
        t0 = time.time()

        # Simulate DoS attack by increasing failure rate and latency
        if dos_attack and random.random() < 0.1:
            node.failure_rate = max(failure_rate, 0.5)
            node.latency = base_latency * 5
        else:
            node.failure_rate = failure_rate
            node.latency = base_latency

        # Simulate burst packet drops
        if burst_drop:
            if burst_active:
                node.failure_rate = p_burst
                burst_counter += 1
                if burst_counter >= burst_len:
                    burst_active = False
                    burst_counter = 0
            elif random.random() < 0.05:
                burst_active = True
                burst_counter = 0

        success = False
        tampered = False
        # Replication for fault tolerance
        for r in range(replication_factor):
            result = await node.send(vote, head)
            if result:
                ok = await head.send(result, capital)
                if ok:
                    success = True
                else:
                    tampered = True
        if success:
            latency = time.time() - t0
            latencies.append(latency)
        if tampered:
            tampered_detected += 1

    end_time = time.time()
    throughput = len(capital.received) / (end_time - start_time)
    avg_latency = statistics.mean(latencies) if latencies else 0
    success_rate = len(capital.received) / votes * 100
    tamper_rate = tampered_detected / votes * 100

    print("\n=== Simulation Summary ===")
    print(f"Total votes: {votes}")
    print(f"Successful votes: {len(capital.received)}")
    print(f"Tampered votes detected: {tampered_detected}")
    print(f"Average latency: {avg_latency:.4f}s")
    print(f"Throughput: {throughput:.2f} votes/sec")
    print(f"Success rate: {success_rate:.2f}%")
    print(f"Tamper rate: {tamper_rate:.2f}%\n")

    return avg_latency, throughput, success_rate, tamper_rate


async def main():
    """
    Demonstrates the simulation under different scenarios:
        - Normal operation
        - DoS attack
        - Burst packet drop
        - Byzantine node with replication
    """
    print("Normal Run:", await simulate(votes=10))
    print("DoS Attack:", await simulate(votes=10, dos_attack=True))
    print("Burst Drop:", await simulate(votes=10, burst_drop=True))
    print(
        "Byzantine Head:",
        await simulate(
            votes=10,
            byzantine_prob=0.05,
            replication_factor=3,
        ),
    )


if __name__ == "__main__":
    asyncio.run(main())
