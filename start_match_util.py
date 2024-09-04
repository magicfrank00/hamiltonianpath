import time
from cons import PORTS
from game.grid import generate_map
import requests
import argparse


def start_game(grid, position, port):
    url = f"http://127.0.0.1:{port}/start"

    data = {"grid": grid, "position": position}

    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())


def start_game_all(grid_size):
    time.sleep(3)  # Wait for all players to start
    grid, entity_position, _ = generate_map(grid_size)
    for port in PORTS:
        start_game(grid, entity_position, port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="Port to use for the server", default="5000")
    args = parser.parse_args()

    grid_size = 4
    grid, entity_position, _ = generate_map(grid_size)
    start_game(grid, entity_position, args.port)
