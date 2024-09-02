import json
import random
from utils import (
    commit_to_graph, open_graph, permute_graph, 
    hash_committed_graph, numrounds, remove_extra_commitments
)

N = 5
cycle = [(0, 4), (4, 2), (2, 3), (3, 1), (1, 0)]
G = [
    [0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0],
    [0, 1, 1, 0, 0],
    [1, 0, 1, 1, 0]
]

def generate_permuted_graph(G, N):
    """Generate a permuted commitment of the graph G."""
    A, openings = commit_to_graph(G, N)
    permutation = random.sample(range(N), N)
    A_permuted = permute_graph(A, N, permutation)
    
    # Sanity checks
    assert G == open_graph(A, N, openings), "Original graph failed to open."
    assert permute_graph(G, N, permutation) == open_graph(A_permuted, N, permute_graph(openings, N, permutation)), "Permuted graph failed to open."

    return A_permuted, openings, permutation

def generate_proofs(G, N, cycle, num_rounds):
    """Generate all proofs needed for the protocol."""
    FS_state = b''
    A_vars, opening_vars, permutation_vars = [], [], []
    
    for i in range(num_rounds):
        print(f"Generating graph {i}")
        A_permuted, openings, permutation = generate_permuted_graph(G, N)
        A_vars.append(A_permuted)
        opening_vars.append(openings)
        permutation_vars.append(permutation)

    # Generate Fiat-Shamir state
    for A_permuted in A_vars:
        FS_state = hash_committed_graph(A_permuted, FS_state)
    
    challenge_bits = bin(int.from_bytes(FS_state, 'big'))[-num_rounds:]
    proofs = []

    for i in range(num_rounds):
        challenge = int(challenge_bits[i])
        A = A_vars[i]
        openings = opening_vars[i]
        permutation = permutation_vars[i]

        if challenge:
            print("Challenge bit is 1")
            permuted_cycle = [[permutation.index(x[0]), permutation.index(x[1])] for x in cycle]
            openings = remove_extra_commitments(openings, N, cycle)
            openings = permute_graph(openings, N, permutation)
            z = [permuted_cycle, openings]
        else:
            print("Challenge bit is 0")
            openings = permute_graph(openings, N, permutation)
            z = [permutation, openings]
        
        proofs.append(json.dumps({"A": A, "z": z}))

    return proofs

# Now send to server
from pwn import process
rem = process(["python3", "server.py"])
proofs = generate_proofs(G, N, cycle, numrounds)
# Send proofs to the remote server
for proof in proofs:
    rem.recvuntil(b"send fiat shamir proof: ")
    rem.sendline(proof)

rem.interactive()
