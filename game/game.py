import pygame
import random
import copy


class GridGame:
    def __init__(
        self,
        send_victory_callback,
        grid,
        entity_position,
        entity_direction,
        move_interval=30,
    ):
        pygame.init()
        self.width = 1200
        self.height = 1200
        self.input_data = (grid, entity_position, entity_direction)
        assert len(grid) == len(grid[0])
        self.grid_size = len(grid)
        self.cell_size = self.width // self.grid_size
        self.border_size = 2
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Grid Game with Arrow Entity")
        self.move_interval = move_interval
        self.game_over = False
        self.send_victory_callback = send_victory_callback
        self.user_cells = []

        self.grid = copy.deepcopy(grid)
        self.entity_position = copy.deepcopy(entity_position)
        self.entity_direction = copy.deepcopy(entity_direction)

        self.entity_color = (255, 255, 255)  # White color for the arrow
        self.tick_count = 0

    def restart_game(self):
        self.color = self.get_random_color()
        self.entity_color = (255, 255, 255)  # White color for the arrow
        self.tick_count = 0
        self.game_over = False
        self.user_cells = []
        self.grid, self.entity_position, self.entity_direction = copy.deepcopy(
            self.input_data
        )

    def get_random_color(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

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
                self.game_over = True
            else:
                self.user_cells.append((new_x, new_y))  # Add the new cell to user_cells

            self.grid[self.entity_position[1]][self.entity_position[0]] = None
            self.entity_position = (new_x, new_y)

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

    def check_victory(self):
        for row in self.grid:
            if any(cell is not None for cell in row):  # Check if any cell is not empty
                return False
        return True

    def display_victory(self):
        font = pygame.font.Font(None, 72)
        text = font.render("Victory! Press R to restart", True, (0, 255, 0))
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
        elif keys[pygame.K_r]:
            self.restart_game()

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.handle_input()

            if not self.game_over:
                if self.tick_count >= self.move_interval:
                    self.update_entity_position()
                    self.tick_count = 0
                    if self.check_victory():
                        self.game_over = True  # Mark the game as over (victory)

                self.draw_grid()
                pygame.display.flip()
                self.tick_count += 1
            else:
                if self.check_victory():  # Display victory message if won
                    self.display_victory()
                    self.send_victory_callback(self.user_cells)
                else:
                    self.display_game_over()

            clock.tick(60)

        pygame.quit()
