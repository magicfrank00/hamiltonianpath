import random
from math import isqrt

def generate_hamiltonian_graph(N):
    # Step 1: Create an empty adjacency matrix
    adjacency_matrix = [[0 for _ in range(N)] for _ in range(N)]

    # Step 2: Create a Hamiltonian cycle
    cycle = list(range(N))
    for i in range(N):
        next_node = (i + 1) % N
        adjacency_matrix[cycle[i]][cycle[next_node]] = 1

    # Step 3: Add random edges to the graph
    num_random_edges = isqrt(random.randint(N, N*(N-1)//2 - N))
    edges_added = 0
    while edges_added < num_random_edges:
        u = random.randint(0, N-1)
        v = random.randint(0, N-1)
        if u != v and adjacency_matrix[u][v] == 0:
            adjacency_matrix[u][v] = 1
            edges_added += 1

    # Step 4: Permute the graph
    permutation = list(range(N))
    random.shuffle(permutation)
    
    permuted_adjacency_matrix = [[0 for _ in range(N)] for _ in range(N)]
    for i in range(N):
        for j in range(N):
            permuted_adjacency_matrix[permutation[i]][permutation[j]] = adjacency_matrix[i][j]
    
    # Permute the cycle
    permuted_cycle = [permutation[i] for i in cycle]

    return permuted_adjacency_matrix, permuted_cycle

# Example usage
N = 30
adj_matrix, hamiltonian_cycle = generate_hamiltonian_graph(N)

# Display the adjacency matrix
print("Adjacency Matrix:")
for row in adj_matrix:
    print(row)

# Display the Hamiltonian cycle
print("\nHamiltonian Cycle:")
print(hamiltonian_cycle)
