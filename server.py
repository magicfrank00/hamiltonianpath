import argparse
from flask import Flask, jsonify, request
from game.game import GridGame
from game.reduction_to_graph import grid_to_adjacency_matrix
from hamiltonian_cycle.client import HamiltonianCycleProver
from hamiltonian_cycle.server import HamiltonianCycleTester
from threading import Thread
import requests

from hamiltonian_cycle.utils import NUM_ROUNDS

app = Flask(__name__)
port = None
ports = [5000, 5001, 5002]


def send_victory(grid, path):
    print("Victory! Path taken:")
    print(grid)
    print(path)
    adj_matrix, graph_path = grid_to_adjacency_matrix(grid, path)
    print("Adjacency Matrix:")
    for row in adj_matrix:
        print(row)
    print("Mapped Graph Path (node indices):", graph_path)

    N = len(adj_matrix)

    prover = HamiltonianCycleProver(N, adj_matrix, graph_path)
    proofs = prover.generate_proofs(NUM_ROUNDS)

    data = {"graph": adj_matrix, "proofs": proofs, "player": port}
    for p in ports:
        if p == port:
            continue
        print(f"Sending to {p}")
        url = f"http://127.0.0.1:{p}/verify"
        try:
            response = requests.post(url, json=data)
            print("Status Code:", response.status_code)
            print("Response JSON:", response.json())
        except Exception as e:
            print(f"Failed to send to {p}: {e}")


@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json()

    if not data or "graph" not in data or "proofs" not in data:
        return jsonify({"error": "No valid data provided"}), 400

    G = data["graph"]
    proofs = data["proofs"]
    player = data["player"][-1]

    try:
        tester = HamiltonianCycleTester(G)

        for i, proof in enumerate(proofs):
            A = proof["A"]
            z = proof["z"]
            tester.loadProof(A, z, i)
        tester.prove_hamiltonian_cycle()
        print(f"Player {player} won!")
        return (
            jsonify({"status": "success", "message": "Hamiltonian cycle is verified"}),
            200,
        )
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)}), 400


@app.route("/start", methods=["POST"])
def start():
    print("Starting game")
    data = request.get_json()

    if not data or "grid" not in data or "position" not in data:
        return jsonify({"error": "No valid data provided"}), 400

    grid = data["grid"]
    position = data["position"]

    try:
        game = GridGame(send_victory, grid, position, "north", None)

        thread = Thread(
            target=game.run,
        )
        thread.start()

        return (
            jsonify({"status": "success", "message": "Hamiltonian cycle is verified"}),
            200,
        )
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)}), 400


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="Port to use for the server", default="5000")
    args = parser.parse_args()
    port = int(args.port)
    app.run(debug=True, port=port)
