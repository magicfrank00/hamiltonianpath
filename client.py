import json
import random
from utils import (
    commit_to_graph,
    open_graph,
    permute_graph,
    hash_committed_graph,
    numrounds,
    remove_extra_commitments,
)
from pwn import process


class HamiltonianCycleProver:
    def __init__(self, N, G, cycle):
        self.N = N
        self.G = G
        self.cycle = cycle

    def generate_permuted_graph(self):
        """Generate a permuted commitment of the graph G."""
        A, openings = commit_to_graph(self.G, self.N)
        permutation = random.sample(range(self.N), self.N)
        A_permuted = permute_graph(A, self.N, permutation)

        # Sanity checks
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

        for i in range(num_rounds):
            print(f"Generating graph {i}")
            A_permuted, openings, permutation = self.generate_permuted_graph()
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
                permuted_cycle = [
                    [permutation.index(x[0]), permutation.index(x[1])]
                    for x in self.cycle
                ]
                openings = remove_extra_commitments(openings, self.N, self.cycle)
                openings = permute_graph(openings, self.N, permutation)
                z = [permuted_cycle, openings]
            else:
                print("Challenge bit is 0")
                openings = permute_graph(openings, self.N, permutation)
                z = [permutation, openings]

            proofs.append(json.dumps({"A": A, "z": z}))

        return proofs

    def send_proofs(self, server_script="server.py"):
        """Send proofs to the server and interact with it."""
        rem = process(["python3", server_script])
        proofs = self.generate_proofs(numrounds)

        for proof in proofs:
            rem.recvuntil(b"send fiat shamir proof: ")
            rem.sendline(proof)

        rem.interactive()


if __name__ == "__main__":
    N = 5
    cycle = [(0, 4), (4, 2), (2, 3), (3, 1), (1, 0)]
    G = [
        [0, 1, 1, 0, 1],
        [1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 1, 1, 0, 0],
        [1, 0, 1, 1, 0],
    ]
    prover = HamiltonianCycleProver(N, G, cycle)
    prover.send_proofs()
