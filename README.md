# Establishing a Secure Voting Network for Local Elections

**Abstract**  
Challenges in e-voting push back its mass adoption by countries. Integrity, verifiability, and resilience to attacks must be enforced, and local elections are the most vulnerable due to their limited information and communication technology (ICT). This paper proposes a balance between cost and security by creating a hierarchical, web-like node structure for network system implementation that includes Software Guard Extension (SGX), virtual private networks (VPN) for transport layer security (TLS) channels, Merkle proofs, and cryptographic safeguards. Blockchain technology is not integrated due to scalability and cost issues, while maintaining the security and redundancy of the proposed architecture. Open source availability of the code and third-party auditing further increase trust in the system, creating a secure, scalable, and verifiable voting model tailored for local elections. Lightweight analytical validation shows average per-vote latency of 186–199 ms across 1k–10k voters under DoS, depending on replication (≈198 ms for r=1 and ≈186–188 ms for r=3). Under normal conditions, average latency is ≈130–141 ms. Replication r=3 sustains ≈99.7% end-to-end success under DoS versus ≈85.7% for r=1, with mild logarithmic growth from Merkle proofs. Network contributes the majority of delay; SGX and verification remain single-digit milliseconds. The validation uses a calibrated closed-form model and reports p95 tails.

---

This repository contains scripts and documentation for a research study on distributed election system reliability and security. The main script performs a comprehensive parameter sweep using network simulation to evaluate how system configuration and adversarial conditions affect performance and correctness.

## Key Features

- Systematically explores combinations of voter count, node failure rate, base network latency, denial-of-service (DoS) attack presence, and replication factor.
- Runs multiple simulation replicates for each parameter set to collect statistics on latency, throughput, success rate, and tamper detection.
- Aggregates results using mean and 95% confidence intervals for robust reporting.
- Outputs results as a CSV file for further analysis and inclusion in research documentation.

## Research Context

- Supports reproducible evaluation of distributed voting systems under realistic network and adversarial scenarios.
- Enables quantitative comparison of system resilience and performance trade-offs.
- Facilitates analysis of fault tolerance mechanisms (e.g., replication) and attack mitigation strategies.

## Usage

1. Run the main script to generate summarized experimental results for each parameter combination. The simulation logic is provided by the `simulate` function in `network_simulation.py`.
2. Output is written to `results/sim_runs.csv` for downstream analysis and visualization.

---

**Author:** Allen Glenn E. Castillo  
**Date:** September 29, 2025
