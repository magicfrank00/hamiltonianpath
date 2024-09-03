import json
from utils import (
    open_graph,
    permute_graph,
    hash_committed_graph,
    test_cycle,
    check_graph,
    check_permutation,
    numrounds,
)


class HamiltonianCycleTester:
    def __init__(self, N, G):
        self.N = N
        self.G = G
        self.FS_state = b""
        self.A_vals = []
        self.z_vals = []

    def prove_hamiltonian_cycle(self):
        print(f"prove to me that G has a hamiltonian cycle!")
        for i in range(numrounds):
            payload = json.loads(input(b"send fiat shamir proof: "))
            A = payload["A"]
            z = payload["z"]

            check_graph(A, self.N)

            self.A_vals.append(A)
            self.z_vals.append(z)

        self.compute_fiat_shamir_challenge()

        for i in range(numrounds):
            print(f"checking round {i}")
            challenge = int(self.challenge_bits[i])
            print(f"challenge bit is {challenge}")
            A = self.A_vals[i]
            z = self.z_vals[i]

            if challenge:
                self.verify_cycle(A, z)
            else:
                self.verify_permutation(A, z)

        print("you've convinced me it has a hamiltonian path! Cool!")

    def compute_fiat_shamir_challenge(self):
        print("computing fiat shamir challenge")
        for i in range(numrounds):
            self.FS_state = hash_committed_graph(self.A_vals[i], self.FS_state)

        self.challenge_bits = bin(int.from_bytes(self.FS_state, "big"))[-numrounds:]

    def verify_cycle(self, A, z):
        cycle, openings = z
        if not test_cycle(A, self.N, cycle, openings):
            print("your proof didn't verify :(")
            exit()
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
            print("your proof didn't verify :(")
            exit()


if __name__ == "__main__":
    N = 5
    G = [
        [0, 1, 1, 0, 1],
        [1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 1, 1, 0, 0],
        [1, 0, 1, 1, 0],
    ]
    proof = HamiltonianCycleProof(N, G)
    proof.prove_hamiltonian_cycle()
