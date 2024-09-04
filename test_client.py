from hamiltonian_cycle.client import HamiltonianCycleProver
from hamiltonian_cycle.generate_graph import generate_hamiltonian_graph
from hamiltonian_cycle.utils import NUM_ROUNDS
import requests

url = "http://127.0.0.1:5000/verify"


N = 5
G, cycle = generate_hamiltonian_graph(N)
prover = HamiltonianCycleProver(N, G, cycle)
proofs = prover.generate_proofs(NUM_ROUNDS)


data = {"graph": G, "proofs": proofs}

response = requests.post(url, json=data)
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
