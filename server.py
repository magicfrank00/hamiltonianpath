from flask import Flask, request, jsonify

from hamiltonian_cycle.server import HamiltonianCycleTester

app = Flask(__name__)


@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json()

    if not data or "graph" not in data or "proofs" not in data:
        return jsonify({"error": "No valid data provided"}), 400

    G = data["graph"]
    proofs = data["proofs"]

    try:
        tester = HamiltonianCycleTester(G)

        for i, proof in enumerate(proofs):
            A = proof["A"]
            z = proof["z"]
            tester.loadProof(A, z, i)
        tester.prove_hamiltonian_cycle()
        return (
            jsonify({"status": "success", "message": "Hamiltonian cycle is verified"}),
            200,
        )
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
