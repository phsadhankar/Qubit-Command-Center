from datetime import datetime
import hashlib
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

# 1. Realistic Desktop Muon Detector Test Data (matching your log format)
TEST_MUON_DATA = open('./logs/data.log').read()

def extract_muon_seed(raw_log: str) -> int:
    """
    Parses the first column (Comp_time: YYYY-MM-DD HH:MM:SS.ffffff),
    computes microsecond inter-arrival deltas between muon hits,
    and hashes them into a uniform 64-bit integer seed.
    """
    timestamps = []
    for line in raw_log.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        # Combine date (parts[0]) and time (parts[1]) for Comp_time
        dt = datetime.strptime(f"{parts[0]} {parts[1]}", "%Y-%m-%d %H:%M:%S.%f")
        timestamps.append(dt)

    if len(timestamps) < 2:
        raise ValueError("Need at least 2 muon timestamps to extract timing deltas.")

    # Compute inter-arrival time differences in microseconds (Poisson entropy)
    deltas_us = [
        int((timestamps[i] - timestamps[i - 1]).total_seconds() * 1_000_000)
        for i in range(1, len(timestamps))
    ]

    # Whiten the entropy pool with SHA-256 and convert to a positive integer seed
    entropy_bytes = ",".join(map(str, deltas_us)).encode("utf-8")
    digest = hashlib.sha256(entropy_bytes).digest()
    return int.from_bytes(digest[:8], byteorder="big")


def run_muon_seeded_circuit(
    circuit: QuantumCircuit, muon_log: str, shots: int = 1024
) -> dict:
    """
    Executes ANY user-provided Qiskit QuantumCircuit seeded by muon arrival times.
    """
    seed = extract_muon_seed(muon_log)
    print(f"Extracted True Random Muon Seed: {seed}")

    # Ensure the circuit has measurement gates
    qc = circuit.copy()
    if qc.num_clbits == 0:
        qc.measure_all()

    # Seed Qiskit's StatevectorSampler with the muon-derived seed
    sampler = StatevectorSampler(seed=seed)
    job = sampler.run([qc], shots=shots)
    result = job.result()[0]

    # Retrieve measurement counts from the classical register
    creg_name = qc.cregs[0].name
    return getattr(result.data, creg_name).get_counts()


# =====================================================================
# DEMO 1: Single-Qubit Hadamard Superposition Circuit
# =====================================================================
hadamard_qc = QuantumCircuit(1, name="Hadamard_Demo")
hadamard_qc.h(0)

print("--- Demo 1: Hadamard Circuit ---")
h_counts = run_muon_seeded_circuit(hadamard_qc, TEST_MUON_DATA, shots=1024)
print("Measurement Counts:", h_counts, "\n")


# =====================================================================
# DEMO 2: Two-Qubit Bell State (Entanglement) Circuit
# =====================================================================
bell_qc = QuantumCircuit(2, name="Bell_State_Demo")
bell_qc.h(0)
bell_qc.cx(0, 1)

print("--- Demo 2: Bell State Entanglement Circuit ---")
bell_counts = run_muon_seeded_circuit(bell_qc, TEST_MUON_DATA, shots=1024)
print("Measurement Counts:", bell_counts)
