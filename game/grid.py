import pygame
import random


class GridGame:
    def __init__(self, width, height, grid_size, move_interval=30):
        pygame.init()
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.cell_size = self.width // self.grid_size
        self.border_size = 2
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Grid Game with Arrow Entity")
        self.move_interval = move_interval
        self.game_over = False
        self.restart_game()

    def restart_game(self):
        self.grid = [
            [None for _ in range(self.grid_size)] for _ in range(self.grid_size)
        ]
        self.color = self.get_random_color()
        self.entity_color = (255, 255, 255)  # White color for the arrow
        self.entity_position, self.entity_direction = self.initialize_entity()
        self.setup_grid()
        self.tick_count = 0
        self.game_over = False

    def get_random_color(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def setup_grid(self):
        start_x, start_y = self.grid_size // 2, self.grid_size // 2
        queue = [(start_x, start_y)]
        steps = random.randint(5, 15)

        while queue and steps > 0:
            x, y = queue.pop(0)
            if self.grid[y][x] is None:
                self.grid[y][x] = self.color
                steps -= 1
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if (
                        0 <= nx < self.grid_size
                        and 0 <= ny < self.grid_size
                        and self.grid[ny][nx] is None
                    ):
                        queue.append((nx, ny))
                        random.shuffle(queue)

    def initialize_entity(self):
        start_x, start_y = self.grid_size // 2, self.grid_size // 2
        position = (start_x, start_y)
        direction = random.choice(["north", "south", "east", "west"])
        return position, direction

    def draw_arrow(self, position, direction):
        x, y = position
        center = (
            x * self.cell_size + self.cell_size // 2,
            y * self.cell_size + self.cell_size // 2,
        )
        size = self.cell_size // 2 - self.border_size
        directions = {
            "north": [
                (
                    center,
                    (center[0] - size, center[1] + size),
                    (center[0] + size, center[1] + size),
                )
            ],
            "south": [
                (
                    center,
                    (center[0] - size, center[1] - size),
                    (center[0] + size, center[1] - size),
                )
            ],
            "east": [
                (
                    center,
                    (center[0] - size, center[1] - size),
                    (center[0] - size, center[1] + size),
                )
            ],
            "west": [
                (
                    center,
                    (center[0] + size, center[1] - size),
                    (center[0] + size, center[1] + size),
                )
            ],
        }
        pygame.draw.polygon(self.screen, self.entity_color, directions[direction][0])

    def update_entity_position(self):
        dx, dy = 0, 0
        if self.entity_direction == "north":
            dy = -1
        elif self.entity_direction == "south":
            dy = 1
        elif self.entity_direction == "east":
            dx = 1
        elif self.entity_direction == "west":
            dx = -1

        new_x = self.entity_position[0] + dx
        new_y = self.entity_position[1] + dy

        if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
            if self.grid[new_y][new_x] is None:
                self.game_over = True  # Mark the game as over
            self.grid[self.entity_position[1]][self.entity_position[0]] = None
            self.entity_position = (new_x, new_y)  # Move onto the square

    def draw_grid(self):
        self.screen.fill((0, 0, 0))  # Clear the screen
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                color = self.grid[row][col]
                if color:
                    pygame.draw.rect(
                        self.screen,
                        color,
                        (
                            col * self.cell_size + self.border_size,
                            row * self.cell_size + self.border_size,
                            self.cell_size - self.border_size * 2,
                            self.cell_size - self.border_size * 2,
                        ),
                    )
                if (col, row) == self.entity_position:
                    self.draw_arrow((col, row), self.entity_direction)

    def display_game_over(self):
        font = pygame.font.Font(None, 72)
        text = font.render("Game Over! Press R to restart", True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.entity_direction = "north"
        elif keys[pygame.K_DOWN]:
            self.entity_direction = "south"
        elif keys[pygame.K_LEFT]:
            self.entity_direction = "west"
        elif keys[pygame.K_RIGHT]:
            self.entity_direction = "east"
        elif keys[pygame.K_r] and self.game_over:
            self.restart_game()

    def run(self):
        running = True
        clock = pygame.time.Clock()  # To manage how fast the screen updates

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.handle_input()

            if not self.game_over:
                if self.tick_count >= self.move_interval:
                    self.update_entity_position()
                    self.tick_count = 0

                self.draw_grid()
                pygame.display.flip()
                self.tick_count += 1
            else:
                self.display_game_over()

            clock.tick(60)  # Limit to 60 ticks per second

        pygame.quit()


if __name__ == "__main__":
    game = GridGame(600, 600, 10)
    game.run()
