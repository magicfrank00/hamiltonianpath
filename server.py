from utils import pedersen_commit, pedersen_open
from utils import commit_to_graph, open_graph, permute_graph
from utils import hash_committed_graph, test_cycle, check_graph
from utils import public_parameters
from utils import check_permutation
from utils import numrounds
import json
import os


N = 5
G = [
    [0,1,1,0,1],
    [1,0,0,0,0],
    [0,0,0,1,0],
    [0,1,1,0,0],
    [1,0,1,1,0]
]

print(f'prove to me that G has a hamiltonian cycle!')

# 128 bit security
FS_state = b''

A_vals = []
z_vals = []
for i in range(numrounds):
    # send permuted commitment matrix
    payload = json.loads(input(b"send fiat shamir proof: "))
    A = payload["A"]
    z = payload["z"]

    check_graph(A,N)

    A_vals.append(A)
    z_vals.append(z)    

print("computing fiat shamir challenge")
for i in range(numrounds):
    FS_state = hash_committed_graph(A_vals[i], FS_state)

challenge_bits = bin(int.from_bytes(FS_state, 'big'))[-numrounds:]

for i in range(numrounds):
    print(f"checking round {i}")
    challenge = int(challenge_bits[i])
    print(f"challenge bit is {challenge}")
    A = A_vals[i]
    z = z_vals[i]
    # Challenge bit is 1:
    # You should open the hamiltonian path
    # z = [cycle, openings of cycle]
    if challenge:
        cycle, openings = z
        if not test_cycle(A, N, cycle, openings):
            print("your proof didn't verify :(")
            exit()
        else:
            print("accepted")
    
    # challenge bit is 0:
    # you should show permutation and open everything
    # z = [permutation, openings of everything]
    else:
        permutation, openings = z
        check_permutation(permutation, N)
        G_permuted = open_graph(A,N, openings)
        G_test = permute_graph(G, N, permutation)
        if G_permuted == G_test:
            print("accepted")
        else:
            print("your proof didn't verify :()")
            exit()
    
print("you've convinced me it has a hamiltonian path! Cool!")
