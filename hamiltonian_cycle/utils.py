import random
from hashlib import sha256

# rfc2409 1024bit prime, generator is 2
P = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE65381FFFFFFFFFFFFFFFF
q = (P - 1) // 2
# generator of order q
g = 2

# h1 = pow(g, random.randint(0,q),P)
# h2 = pow(g, random.randint(0,q),P)
h1 = 0x85D03CBA7458546B596089E9169486E4353C6BFAB79CC9DF56AFEAA837F66CDE6AC5EC344613F978A4257D46E6B7D11DEABC9D48BA5C6669B036E774B41738ADAA24B1EE31DFEB5F076974DD76CEF5C84023B16BA54AAB0E2D01DF43709534D8E71C781AA279D3B13BCA7C4E3EE2EA10E3D436AA3DCD12807E23C5FC0BBDFDD4
h2 = 0x12371F548E2981078AF9D58915BA7A9F89207F0F00574FEC853DC2201A8FF2DFA626C7A96E8FB4D032E5BA613E898C34E5CE121EDA694BC9AA010B186959BB2BFA7E2C12B9D3E9505ED60A1F4042A96860F500A2A64AEAD69E604C09ADC4BD85789183775C3B15792C35E905ABFB3B7A6335C7D5235309C81FE84CAC815D4948
public_parameters = P, q, h1, h2

NUM_ROUNDS = 50 # security parameter


def pedersen_commit(message, params=public_parameters):
    P, q, h1, h2 = params
    r = random.randint(0, q)
    commitment = (pow(h1, message, P) * pow(h2, r, P)) % P
    return commitment, r


def pedersen_open(commitment, message, r, params=public_parameters):
    P, q, h1, h2 = params
    return commitment == (pow(h1, message, P) * pow(h2, r, P)) % P


def commit_to_graph(G, N):
    """Commit each entry in the graph with a Pedersen commitment and return the commitment matrix and the openings."""
    comm_mat = [[0] * N for _ in range(N)]
    openings_mat = [[0] * N for _ in range(N)]

    for i in range(N):
        for j in range(N):
            m = G[i][j]
            comm, r = pedersen_commit(m)
            assert pedersen_open(comm, m, r), f"Failed to open {m} {r}"
            comm_mat[i][j] = comm
            openings_mat[i][j] = [m, r]

    return comm_mat, openings_mat


def is_valid_graph(G, N):
    """Check that G is a valid adjacency matrix."""
    assert len(G) == N, "G has wrong size"
    for row in G:
        assert len(row) == N, "G has wrong size"
    return True


def open_graph(comm_mat, N, openings_mat):
    """Given a commitment matrix and the respective openings, return the committed graph."""
    G = [[0] * N for _ in range(N)]

    for i in range(N):
        for j in range(N):
            comm = comm_mat[i][j]
            m, r = openings_mat[i][j]
            assert pedersen_open(comm, m, r)
            G[i][j] = m

    return G

# path is just a sequence of nodes 
def __check_valid_hamiltonian_path(N, hamiltonian_path):
    """Check that the path is in the form [a, b, c, ..., z]."""
    assert len(hamiltonian_path) == N
    assert sorted(hamiltonian_path) == list(range(N))


def test_path(committed_graph, N, hamiltonian_path, openings_mat):
    """Test that the nodes form a Hamiltonian cycle in the graph."""
    __check_valid_hamiltonian_path(N, hamiltonian_path)

    # Check that the commitments in the path open correctly as 1
    for i in range(N-1):
        src, dst = hamiltonian_path[i],hamiltonian_path[i+1]
        m, r = openings_mat[src][dst]
        assert m == 1
        assert pedersen_open(committed_graph[src][dst], m, r)

    return True


def permute_graph(G, N, permutation):
    """Permute the graph using the permutation."""
    return [[G[permutation[i]][permutation[j]] for j in range(N)] for i in range(N)]


def remove_extra_commitments(openings, N, path):
    """Extract the subset of randomness values needed to open only the commitments of the path."""
    new_openings = [[[0xDEADBEEF, 0xDEADBEEF] for _ in range(N)] for _ in range(N)]
    edges = [(path[i], path[i+1]) for i in range(N-1)]
    for x in edges:
        m, r = openings[x[0]][x[1]]
        new_openings[x[0]][x[1]] = [m, r]

    return new_openings


def hash_committed_graph(G, state):
    """Iterated Fiat-Shamir: Take previous state and current graph, and return new hash."""
    fs_state = sha256(state)
    fs_state.update(str(G).encode())
    return fs_state.digest()


def check_permutation(perm, N):
    """Check if permutation is valid."""
    assert len(perm) == N
    for i in range(N):
        assert i in perm
    return True
