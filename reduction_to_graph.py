def grid_to_adjacency_matrix(grid, path):
    # Step 1: Flatten the grid and assign indices to valid nodes
    node_map = {}
    index = 0
    rows, cols = len(grid), len(grid[0])

    for y in range(rows):
        for x in range(cols):
            if grid[y][x] is not None:
                node_map[(x, y)] = index
                index += 1

    total_nodes = len(node_map)
    # Initialize adjacency matrix as a 2D list of zeros
    adj_matrix = [[0 for _ in range(total_nodes)] for _ in range(total_nodes)]

    # Step 2: Create the adjacency matrix by linking valid neighbors
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Down, Right, Up, Left
    for (x, y), idx in node_map.items():
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (nx, ny) in node_map:
                neighbor_idx = node_map[(nx, ny)]
                adj_matrix[idx][neighbor_idx] = 1
                adj_matrix[neighbor_idx][idx] = 1  # It's an undirected graph

    # Step 3: Map the path to the adjacency matrix using node indices
    graph_path = [node_map[coord] for coord in path]

    return adj_matrix, graph_path


# Example usage
grid = [
    [None, (247, 108, 120), (247, 108, 120), (247, 108, 120)],
    [None, (247, 108, 120), (247, 108, 120), (247, 108, 120)],
    [None, None, (247, 108, 120), (247, 108, 120)],
    [None, None, (247, 108, 120), (247, 108, 120)],
]

path = [(3, 0), (2, 0), (1, 0), (1, 1), (2, 1), (3, 1), (3, 2), (3, 3), (2, 3), (2, 2)]

adj_matrix, graph_path = grid_to_adjacency_matrix(grid, path)

print("Adjacency Matrix:")
for row in adj_matrix:
    print(row)
print("Mapped Graph Path (node indices):", graph_path)
