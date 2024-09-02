import random
from hashlib import sha256

# rfc2409 1024bit prime, generator is 2
P = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE65381FFFFFFFFFFFFFFFF 
q = (P-1)//2
# generator of order q
g = 2 

# h1 = pow(g, random.randint(0,q),P)
# h2 = pow(g, random.randint(0,q),P)
h1 = 0x85d03cba7458546b596089e9169486e4353c6bfab79cc9df56afeaa837f66cde6ac5ec344613f978a4257d46e6b7d11deabc9d48ba5c6669b036e774b41738adaa24b1ee31dfeb5f076974dd76cef5c84023b16ba54aab0e2d01df43709534d8e71c781aa279d3b13bca7c4e3ee2ea10e3d436aa3dcd12807e23c5fc0bbdfdd4
h2 = 0x12371f548e2981078af9d58915ba7a9f89207f0f00574fec853dc2201a8ff2dfa626c7a96e8fb4d032e5ba613e898c34e5ce121eda694bc9aa010b186959bb2bfa7e2c12b9d3e9505ed60a1f4042a96860f500a2a64aead69e604c09adc4bd85789183775c3b15792c35e905abfb3b7a6335c7d5235309c81fe84cac815d4948
public_parameters = P,q,h1,h2

numrounds = 50


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


def check_graph(G, N):
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


def __check_valid_hamiltonian_path(N, hamiltonian_path):
    """Check that the path is in the form [(a,b), (b,c), ..., (z,a)]."""
    assert len(hamiltonian_path) == N
    from_list = [n[0] for n in hamiltonian_path]
    to_list = [n[1] for n in hamiltonian_path]

    for i in range(N):
        assert i in from_list
        assert i in to_list
        assert hamiltonian_path[i][1] == hamiltonian_path[(i + 1) % N][0]


def test_cycle(committed_graph, N, hamiltonian_path, openings_mat):
    """Test that the nodes form a Hamiltonian cycle in the graph."""
    __check_valid_hamiltonian_path(N, hamiltonian_path)

    # Check that the commitments in the path open correctly as 1
    for i in range(N):
        src, dst = hamiltonian_path[i]
        m, r = openings_mat[src][dst]
        assert m == 1
        assert pedersen_open(committed_graph[src][dst], m, r)

    return True


def permute_graph(G, N, permutation):
    """Permute the graph using the permutation."""
    return [[G[permutation[i]][permutation[j]] for j in range(N)] for i in range(N)]


def remove_extra_commitments(openings, N, cycle):
    """Extract the subset of randomness values needed to open only the commitments of the path."""
    new_openings = [[[0xdeadbeef, 0xdeadbeef] for _ in range(N)] for _ in range(N)]

    for x in cycle:
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