from game.game import GridGame
from game.grid import generate_map


def send_victory(path):
    print("Victory! Path taken:")
    for p in path:
        print(p)


if __name__ == "__main__":
    grid_size = 10
    steps_range = (5, 15)  # Number of colored cells range

    grid, entity_position, entity_direction = generate_map(grid_size, steps_range)
    game = GridGame(send_victory, grid, entity_position, entity_direction)
    game.run()
