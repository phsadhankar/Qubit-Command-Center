# Qubit Command Center

A quantum circuit execution seeded by real muon arrival timing data.

## What it does

`main.py` parses a desktop muon detector log (`logs/data.log`), computes the
inter-arrival time deltas between muon hits, hashes them with SHA-256, and
uses the result as a random seed for Qiskit's `StatevectorSampler`.

Two demos are included:

- **Demo 1:** single-qubit Hadamard superposition circuit
- **Demo 2:** two-qubit Bell state (entanglement) circuit

## Requirements

- Python 3.10+
- Qiskit installed

## Running

```
.venv\Scripts\activate
python main.py
```
