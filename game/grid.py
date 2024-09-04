import random
import time


def generate_map(grid_size):
    grid = [[None for _ in range(grid_size)] for _ in range(grid_size)]

    # Random starting point on an edge
    start_x, start_y = random.choice(
        [
            (0, random.randint(0, grid_size - 1)),
            (grid_size - 1, random.randint(0, grid_size - 1)),
            (random.randint(0, grid_size - 1), 0),
            (random.randint(0, grid_size - 1), grid_size - 1),
        ]
    )

    # Path generation variables
    current_position = (start_x, start_y)
    grid[start_y][start_x] = (
        random.randint(200, 255),
        random.randint(100, 150),
        random.randint(100, 150),
    )
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Down, right, up, left
    path = [current_position]

    def is_valid_move(x, y):
        return 0 <= x < grid_size and 0 <= y < grid_size and grid[y][x] is None

    def has_unvisited_neighbors(x, y):
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if is_valid_move(nx, ny):
                return True
        return False

    # Generate the path
    while len(path) < grid_size * grid_size * 0.6:  # Fill roughly 60% of the grid
        x, y = current_position
        random.shuffle(directions)

        unvisited_neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if is_valid_move(nx, ny):
                unvisited_neighbors.append((nx, ny))

        if unvisited_neighbors:
            # Randomly choose an unvisited neighbor
            next_x, next_y = random.choice(unvisited_neighbors)
            grid[next_y][next_x] = grid[y][x]
            path.append((next_x, next_y))
            current_position = (next_x, next_y)
        else:
            # Backtrack to previous point if stuck
            if len(path) > 1:
                path.pop()
                current_position = path[-1]

    # Make sure the path is valid by avoiding dead ends
    for i in range(len(path)):
        x, y = path[i]
        if (
            not has_unvisited_neighbors(x, y)
            and len(path) < grid_size * grid_size * 0.6
        ):
            if i != 0:
                path = path[:i]  # Cut off the invalid portion of the path
                break

    starting_point = path[0]
    print(grid)

    # Time-limited solution search
    start_time = time.time()
    path = find_solution(grid, starting_point, start_time)
    print(path)

    if not path:
        print("not found hmmm")
        return generate_map(grid_size)
    return grid, starting_point, path


def find_solution(grid, start_position, start_time, time_limit=1):
    print("finding solution...")
    grid_size = len(grid)
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Down, right, up, left
    solution_path = []
    visited = set()

    def is_valid_move(x, y):
        return (
            0 <= x < grid_size
            and 0 <= y < grid_size
            and grid[y][x] is not None
            and (x, y) not in visited
        )

    def backtrack(x, y):
        # Check if time limit exceeded
        if time.time() - start_time > time_limit:
            return False

        visited.add((x, y))
        solution_path.append((x, y))

        if len(visited) == sum(
            sum(1 for cell in row if cell is not None) for row in grid
        ):
            return True

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if is_valid_move(nx, ny):
                if backtrack(nx, ny):
                    return True

        visited.remove((x, y))
        solution_path.pop()
        return False

    start_x, start_y = start_position
    if backtrack(start_x, start_y):
        return solution_path
    else:
        return None  # No valid solution found
