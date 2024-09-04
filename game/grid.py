import random


def generate_map(grid_size, steps_range):
    grid = [[None for _ in range(grid_size)] for _ in range(grid_size)]
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    start_x, start_y = grid_size // 2, grid_size // 2
    queue = [(start_x, start_y)]
    steps = random.randint(*steps_range)

    while queue and steps > 0:
        x, y = queue.pop(0)
        if grid[y][x] is None:
            grid[y][x] = color
            steps -= 1
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[ny][nx] is None:
                    queue.append((nx, ny))
                    random.shuffle(queue)

    start_x, start_y = grid_size // 2, grid_size // 2
    position = (start_x, start_y)
    direction = random.choice(["north", "south", "east", "west"])

    return grid, position, direction
