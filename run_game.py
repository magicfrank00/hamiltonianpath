from game.game import GridGame
from game.grid import generate_map
from reduction_to_graph import grid_to_adjacency_matrix


def send_victory(path):
    print("Victory! Path taken:")
    print(grid)
    print(path)
    adj_matrix, graph_path = grid_to_adjacency_matrix(grid, path)
    print("Adjacency Matrix:")
    for row in adj_matrix:
        print(row)
    print("Mapped Graph Path (node indices):", graph_path)

    # for p in path:
    #     print(p)


if __name__ == "__main__":
    grid_size = 7

    grid, entity_position, solution = generate_map(grid_size)
    game = GridGame(send_victory, grid, entity_position, "north", solution)
    game.run()
