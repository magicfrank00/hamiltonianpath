from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import json
import random
import time
from .server import HamiltonianCycleTester
from .utils import (
    commit_to_graph,
    open_graph,
    permute_graph,
    hash_committed_graph,
    NUM_ROUNDS,
    remove_extra_commitments,
)


class HamiltonianCycleProver:
    def __init__(self, N, G, path):
        self.N = N
        self.G = G
        self.path = path

    def generate_permuted_graph(self):
        """Generate a permuted commitment of the graph G."""
        A, openings = commit_to_graph(self.G, self.N)
        permutation = random.sample(range(self.N), self.N)
        A_permuted = permute_graph(A, self.N, permutation)

        # Sanity checks, expensive so sampling
        if random.random() < 0.01:
            assert self.G == open_graph(
                A, self.N, openings
            ), "Original graph failed to open."
            assert permute_graph(self.G, self.N, permutation) == open_graph(
                A_permuted, self.N, permute_graph(openings, self.N, permutation)
            ), "Permuted graph failed to open."

        return A_permuted, openings, permutation

    def generate_proofs(self, num_rounds):
        """Generate all proofs needed for the protocol."""
        FS_state = b""
        A_vars, opening_vars, permutation_vars = [], [], []

        with ProcessPoolExecutor(max_workers=16) as executor:
            futures = [
                executor.submit(self.generate_permuted_graph) for _ in range(num_rounds)
            ]
            for i, future in enumerate(as_completed(futures)):
                print(f"Graph {i} generated")
                A_permuted, openings, permutation = future.result()
                A_vars.append(A_permuted)
                opening_vars.append(openings)
                permutation_vars.append(permutation)

        # Generate Fiat-Shamir state
        for A_permuted in A_vars:
            FS_state = hash_committed_graph(A_permuted, FS_state)

        challenge_bits = bin(int.from_bytes(FS_state, "big"))[-num_rounds:]
        proofs = []

        for i in range(num_rounds):
            challenge = int(challenge_bits[i])
            A = A_vars[i]
            openings = opening_vars[i]
            permutation = permutation_vars[i]

            if challenge:
                print("Challenge bit is 1")

                permuted_path = [permutation.index(node) for node in self.path]
                openings = remove_extra_commitments(openings, self.N, self.path)
                openings = permute_graph(openings, self.N, permutation)
                z = [permuted_path, openings]
            else:
                print("Challenge bit is 0")
                openings = permute_graph(openings, self.N, permutation)
                z = [permutation, openings]

            proofs.append({"A": A, "z": z})

        return proofs


if __name__ == "__main__":
    N = 5
    path = [(0, 4), (4, 2), (2, 3), (3, 1)]
    G = [
        [0, 1, 1, 0, 1],
        [1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 1, 1, 0, 0],
        [1, 0, 1, 1, 0],
    ]
    prover = HamiltonianCycleProver(N, G, path)
    tester = HamiltonianCycleTester(G)
    proofs = prover.generate_proofs(NUM_ROUNDS)

    for i, proof in enumerate(proofs):
        A = proof["A"]
        z = proof["z"]
        tester.loadProof(A, z, i)
    tester.prove_hamiltonian_cycle()
