from game.game import GridGame
from game.grid import generate_map


def send_victory(path):
    print("Victory! Path taken:")
    for p in path:
        print(p)


if __name__ == "__main__":
    grid_size = 7

    grid, entity_position, solution = generate_map(grid_size)
    game = GridGame(send_victory, grid, entity_position, 'north', solution)
    game.run()
