import argparse
import threading
from flask import Flask, jsonify, request
from cons import GRID_SIZE, PORTS
from game.game import GridGame
from game.reduction_to_graph import grid_to_adjacency_matrix
from hamiltonian_cycle.client import HamiltonianCycleProver
from hamiltonian_cycle.server import HamiltonianCycleTester
from threading import Thread
import requests

from hamiltonian_cycle.utils import NUM_ROUNDS
from start_match_util import start_game_all

from queue import Queue


app = Flask(__name__)
port = None

event_queue = Queue()


def send_request(p, data, url):
    try:
        response = requests.post(url, json=data)
        print(f"Sending to {p}")
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())
    except Exception as e:
        if "Connection refused" in str(e):
            print("Player not running")
        else:
            print(f"Failed to send to {p}: {e}")


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

    event_queue.put(f"Victory! Generating proofs")
    prover = HamiltonianCycleProver(N, adj_matrix, graph_path)
    proofs = prover.generate_proofs(NUM_ROUNDS)

    data = {"graph": adj_matrix, "proofs": proofs, "player": port}
    for p in PORTS:
        if p == port:
            continue
        print(f"Sending to {p}")
        url = f"http://127.0.0.1:{p}/verify"
        thread = threading.Thread(target=send_request, args=(p, data, url))
        thread.start()
    event_queue.put(f"Sent victory to other players")


def send_victory_thread(grid, path):
    thread = Thread(
        target=send_victory,
        args=(grid, path),
    )
    thread.start()


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
        event_queue.put(f"Player {player} won!")
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
        game = GridGame(send_victory_thread, grid, position, "north", None, event_queue)

        thread = Thread(
            target=game.run,
        )
        thread.start()

        return (
            jsonify({"status": "success", "message": "Starting player" + port}),
            200,
        )
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)}), 400


@app.route("/match", methods=["GET"])
def match():
    print("Generating a match")
    try:
        thread = Thread(
            target=start_game_all,
            args=(GRID_SIZE,),
        )
        thread.start()

        return (
            jsonify({"status": "success", "message": "Starting match"}),
            200,
        )
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)}), 400


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", help="Player 0,1,2", default="0")
    args = parser.parse_args()
    player = args.p
    port = PORTS[int(player)]
    app.run(debug=True, port=port)
