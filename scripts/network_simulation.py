import asyncio
import random
import time
import statistics


class Node:
    def __init__(self, name, failure_rate=0.0, latency=0.01, jitter=False):
        self.name = name
        self.failure_rate = failure_rate
        self.latency = latency
        self.jitter = jitter

    async def send(self, data, next_node):
        lat = self.latency
        if self.jitter:
            lat += random.uniform(0, self.latency)
        await asyncio.sleep(lat)
        if random.random() < self.failure_rate:
            return None
        return await next_node.receive(data)

    async def receive(self, data):
        lat = self.latency
        if self.jitter:
            lat += random.uniform(0, self.latency)
        await asyncio.sleep(lat)
        return data


class Head(Node):
    def __init__(self, name, latency=0.01, byzantine_prob=0.0, jitter=False):
        super().__init__(name, latency=latency, jitter=jitter)
        self.byzantine_prob = byzantine_prob

    async def receive(self, data):
        if self.byzantine_prob > 0 and random.random() < self.byzantine_prob:
            data = f"{data}-tampered"
        return await super().receive(data)


class Capital(Node):
    def __init__(self, name):
        super().__init__(name)
        self.received = []
        self.tampered = 0

    async def receive(self, data):
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

        if dos_attack and random.random() < 0.1:
            node.failure_rate = max(failure_rate, 0.5)
            node.latency = base_latency * 5
        else:
            node.failure_rate = failure_rate
            node.latency = base_latency

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
