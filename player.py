from game.grid import generate_map
import requests


import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="Port to use for the server", default="5000")
    args = parser.parse_args()

    grid_size = 4
    grid, entity_position, _ = generate_map(grid_size)

    url = f"http://127.0.0.1:{args.port}/start"

    data = {"grid": grid, "position": entity_position}

    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
