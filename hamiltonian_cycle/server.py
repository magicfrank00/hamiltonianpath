from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import time
from .utils import (
    open_graph,
    permute_graph,
    hash_committed_graph,
    test_path,
    is_valid_graph,
    check_permutation,
    NUM_ROUNDS,
)


class HamiltonianCycleTester:
    def __init__(self, G):
        self.G = G
        assert len(G) == len(G[0])
        self.N = len(G)
        self.FS_state = b""
        self.A_vals = []
        self.z_vals = []
        self.current_round = 0

    def loadProof(self, A, z, round_n):
        """<Loads the proof for a specific round."""
        if round_n != self.current_round:
            raise ValueError(
                f"Round {round_n} is out of sequence. Current round is {self.current_round}."
            )

        is_valid_graph(A, self.N)

        self.A_vals.append(A)
        self.z_vals.append(z)

        self.current_round += 1

    def verify_round(self, i):
        print(f"checking round {i}")
        challenge = int(self.challenge_bits[i])
        print(f"challenge bit is {challenge}")
        A = self.A_vals[i]
        z = self.z_vals[i]

        if challenge:
            return self.verify_cycle(A, z)
        else:
            return self.verify_permutation(A, z)

    def prove_hamiltonian_cycle(self):
        print(f"prove to me that G has a hamiltonian cycle!")
        if self.current_round != NUM_ROUNDS:
            raise ValueError(
                f"Expected {NUM_ROUNDS} rounds, but only received {self.current_round}."
            )

        assert len(self.A_vals) == NUM_ROUNDS

        self.compute_fiat_shamir_challenge()
        with ProcessPoolExecutor() as executor:
            futures = {
                executor.submit(self.verify_round, i): i for i in range(NUM_ROUNDS)
            }

            for future in as_completed(futures):
                round_index = futures[future]
                result = future.result()
                print(
                    f"Round {round_index} verification complete with result: {result}"
                )

        print("you've convinced me it has a hamiltonian path! Cool!")

    def compute_fiat_shamir_challenge(self):
        print("computing fiat shamir challenge")
        for i in range(NUM_ROUNDS):
            self.FS_state = hash_committed_graph(self.A_vals[i], self.FS_state)

        self.challenge_bits = bin(int.from_bytes(self.FS_state, "big"))[-NUM_ROUNDS:]

    def verify_cycle(self, A, z):
        cycle, openings = z
        if not test_path(A, self.N, cycle, openings):
            raise Exception("your proof didn't verify :(")
        else:
            print("accepted")

    def verify_permutation(self, A, z):
        permutation, openings = z
        check_permutation(permutation, self.N)
        G_permuted = open_graph(A, self.N, openings)
        G_test = permute_graph(self.G, self.N, permutation)
        if G_permuted == G_test:
            print("accepted")
        else:
            raise Exception("your proof didn't verify :(")
