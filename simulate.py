from client import HamiltonianCycleProver
from generate_graph import generate_hamiltonian_graph
from server import HamiltonianCycleTester
from utils import numrounds

N = 5
G, cycle = generate_hamiltonian_graph(N)
prover = HamiltonianCycleProver(N, G, cycle)
tester = HamiltonianCycleTester(G)
proofs = prover.generate_proofs(numrounds)

for i, proof in enumerate(proofs):
    A = proof["A"]
    z = proof["z"]
    tester.loadProof(A, z, i)
tester.prove_hamiltonian_cycle()
